import json
import shutil
from pathlib import Path
import time
from pesto.common.pesto import PESTO_WORKSPACE
from pesto.common.testing import logger
from pesto.common.testing.payload_generator import PayloadGenerator
from pesto.common.testing.service_manager import ServiceManager
from pesto.common.testing.service_tester import ServiceTester

TMP_PATH = Path("/tmp/pesto/")


class TestRunner:
    def __init__(self, docker_image_name: str, network: str = None, nvidia=False):
        self.docker_image_name = docker_image_name
        self.nvidia = nvidia
        self.network = network

        image, tag = self.docker_image_name.split(":")

        self._tmp_test_resources = TMP_PATH / "tests" / image / tag
        self._test_output = Path(PESTO_WORKSPACE) / "tests" / image / tag

    def prepare_resources(self, test_resources_path: Path):

        tests = []
        describe = {}

        shutil.rmtree(self._tmp_test_resources, ignore_errors=True)
        self._tmp_test_resources.mkdir(exist_ok=True, parents=True)

        for path in sorted(test_resources_path.iterdir()):

            if path.is_dir() and "test_" in path.stem:
                test_dir = path.stem
                shutil.rmtree(self._tmp_test_resources / test_dir, ignore_errors=True)
                shutil.copytree(path, self._tmp_test_resources / test_dir)

                tests.append(self._tmp_test_resources / test_dir)

            elif path.is_file() and path.match("*describe*.json"):
                with open(path, 'r') as f:
                    describe = json.load(f)

        return tests, describe

    def run_all(self, test_resources_path: Path):
        tests, expected_describe = self.prepare_resources(test_resources_path)

        if self.nvidia:
            logger.info("Running with nvidia runtime")

        with ServiceManager(
                docker_image=self.docker_image_name,
                nvidia=self.nvidia,
                attach_when_running=True,
                image_volume_path="/tmp/",
                host_volume_path="/tmp"
        ) as service:

            # force restarting service
            if service._existing_container:
                logger.debug("Force restarting service to ensure resources properly mounted")
                service.stop()
                time.sleep(10)
                service.run()
                time.sleep(5)

            service_tester = ServiceTester(server_url=service.server_url)

            all_results = dict()

            # Save describes for debug
            with open(self._tmp_test_resources / "expected_describe.json", "w") as f:
                json.dump(expected_describe, f, indent=2)

            with open(self._tmp_test_resources / "actual_describe.json", "w") as f:
                actual_describe = service_tester.endpoint_manager.describe
                json.dump(actual_describe, f, indent=2)

            # Validate describe
            describe_differences = service_tester.validate_describe(expected_describe)

            all_results['describe'] = describe_differences

            for test_dir in tests:
                payload = PayloadGenerator(images_as_base64=False).generate(str(test_dir / "input"))
                with open('/tmp/test.json','w') as f:
                    json.dump(payload, f)
                
                expected = PayloadGenerator(images_as_base64=False).generate(str(test_dir / "output"))

                response, validation_results = service_tester.validate_process(payload, expected)

                all_results[test_dir.stem] = validation_results

                # Serialize response for debug
                response_path = test_dir / "response"
                with open(test_dir / "response.json", "w") as f:
                    json.dump(response, f, indent=2)

                self._serialize_response(response_path, response)

        with open(self._tmp_test_resources / "results.json", "w") as f:
            json.dump(all_results, f, indent=2)

        logger.info("--- Tests Results ---")
        logger.info(json.dumps(all_results, indent=2))
        logger.info("--- Copying tests outputs to {}".format(self._tmp_test_resources))
        shutil.rmtree(self._test_output, ignore_errors=True)
        shutil.copytree(self._tmp_test_resources, self._test_output)

        return all_results

    @staticmethod
    def _serialize_response(response_path: Path, response: dict):
        def _is_uri(val):
            if isinstance(val, str) and (val.startswith("file://") or val.startswith("/")) and Path(val).exists():
                return True
            else:
                return False

        def _write_val(val, path):
            if not _is_uri(val):
                with open(path, 'w') as f:
                    if isinstance(val, dict):
                        f.write(json.dumps(val, indent=2))
                    else:
                        f.write(str(val))
            else:
                shutil.copy(val, "{}{}".format(path, Path(val).suffix))

        response_path.mkdir(exist_ok=True)
        for key in response:
            if isinstance(response[key], list):
                (response_path / key).mkdir(exist_ok=True)
                [_write_val(_val, response_path / str(key) / str(i)) for i, _val in enumerate(response[key])]
            else:
                _write_val(response[key], response_path / str(key))
