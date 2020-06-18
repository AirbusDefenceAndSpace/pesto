from pathlib import Path
import json

from pesto.common.testing.endpoint_manager import EndpointManager
from pesto.common.testing.payload_generator import PayloadGenerator
from pesto.common.testing.service_manager import ServiceManager
from pesto.common.testing.service_tester import ServiceTester

port = 4000
service = "{{cookiecutter.project_sname}}:{{cookiecutter.project_version}}"
# service = "{{cookiecutter.project_sname}}:{{cookiecutter.project_version}}-stateful" # test stateful profile
nvidia = "gpu" in service

test_dir = Path(__file__).parent.parent / "pesto" "/tests"

print("Running in {}".format(test_dir))

test_files_in = test_dir / "resources" / "test_1" / "input"
test_files_out = test_dir / "resources" / "test_1" / "output"

with ServiceManager(docker_image=service, host_port=port, nvidia=nvidia) as service:
    # # Attach to logs in a subprocess
    # service.attach()

    # Wrapper around pesto endpoints to manage get & post requests
    endpoints = EndpointManager(server_url=service.server_url)

    # Tester utils to compare payloads / responses against expected values
    service_tester = ServiceTester(server_url=service.server_url)

    # check that the server is alive
    print(endpoints.is_alive)

    # get describe
    print(endpoints.describe)

    # validate describe
    with open(test_dir / "resources" / "expected_describe.json", "r") as f:
        expected = json.load(f)
        diff = service_tester.validate_describe(expected)

    print(diff)

    # generate input payload
    payload = PayloadGenerator(images_as_base64=True).generate(str(test_files_in))

    # generate expected response payload
    expected = PayloadGenerator(images_as_base64=False).generate(str(test_files_out))

    # send processing request with payload
    response = endpoints.process(payload)
    print(response)

    # validate response against expected response
    response, results = service_tester.validate_process(payload, expected)

    print(results)
