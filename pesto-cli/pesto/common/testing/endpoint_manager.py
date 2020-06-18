import json
import time
from tempfile import NamedTemporaryFile

import requests
from pesto.common.testing import logger
from pesto.common.utils import truncate_dict_for_debug
from pesto.ws.features.converter.image.image import Image


class EndpointManager:
    def __init__(self, server_url):
        self.server_url = server_url
        self._describe = None

    @property
    def is_alive(self) -> bool:
        try:
            response = requests.get("{}/api/v1/health".format(self.server_url))

            return response.status_code == 200
        except:
            return False

    @property
    def describe(self) -> dict:
        if not self._describe:
            self._describe = requests.get(url="{}/api/v1/describe".format(self.server_url)).json()
        return self._describe

    @property
    def stateful(self) -> bool:
        return self.describe.get("asynchronous")

    @property
    def input_schema(self) -> dict:
        return self.describe.get("input")

    @property
    def output_schema(self) -> dict:
        return self.describe.get("output")

    def process(self, payload: dict) -> dict:
        logger.debug(json.dumps(truncate_dict_for_debug(payload), indent=2))
        response = requests.post(url="{}/api/v1/process".format(self.server_url), json=payload)

        if self.stateful:
            status_url = response.json()["link"]
            job_id = status_url.split("/")[-2]
            job = _StatefulJob(
                server_url=self.server_url,
                job_id=job_id,
                output_schema=self.output_schema,
            )
            if job.wait_done():
                result = job.result
            else:
                result = {"status": "PROCESSING ERROR"}
        else:
            job = _StatelessJob(response=response)
            result = job.result

        logger.debug(json.dumps(truncate_dict_for_debug(result), indent=2))
        return result


class _StatelessJob:
    """
    Internal class to parse results from a stateless job
    """

    def __init__(self, response):
        self.response = response

    @property
    def result(self):
        return self.response.json()


class _StatefulJob:
    """
    Internal class to parse results from a stateful job
    """

    def __init__(self, server_url, job_id, output_schema):
        self.server_url = server_url
        self.job_id = job_id
        self.output_schema = output_schema

    @property
    def status_url(self):
        return "{}/api/v1/jobs/{}/status".format(self.server_url, self.job_id)

    @property
    def results_url(self):
        return "{}/api/v1/jobs/{}/results".format(self.server_url, self.job_id)

    @property
    def is_done(self):
        status = requests.get(self.status_url).json().get("status")
        return status == "DONE"

    def wait_done(self, max_tries=20):
        num_tries = 0
        while (num_tries < max_tries) and (not self.is_done):
            logger.info("Waiting for job to complete")
            num_tries += 1
            time.sleep(2)

        if num_tries < max_tries:
            logger.info("Job complete")
            return True
        else:
            logger.error("Timeout reached")
            return False

    @property
    def result(self):
        result = requests.get(self.results_url).json()
        result = self._parse_result(result)
        return result

    def _parse_result(self, result: dict):
        parsed_result = dict()
        for key in result:
            link_type = self._compute_type(key)
            val = result.get(key)
            if self._is_uri(val):
                if isinstance(val, list):
                    parsed_result[key] = [self._get_result(uri, link_type) for uri in val]
                else:
                    parsed_result[key] = self._get_result(val, link_type)
            else:
                parsed_result[key] = val

        return parsed_result

    @staticmethod
    def _get_result(uri, key_type):
        response = requests.get(uri)
        content_type = response.headers["Content-Type"]

        if key_type == "#/definitions/Images":
            driver = content_type.split("/")[-1]
            path = "{}.{}".format(NamedTemporaryFile().name, driver)
            result = Image.from_bytes(response.content).to_path(path)
        elif key_type == "#/definitions/Image":
            driver = content_type.split("/")[-1]
            path = "{}.{}".format(NamedTemporaryFile().name, driver)
            result = Image.from_bytes(response.content).to_path(path)
        elif key_type in [
            "#/definitions/Metadata",
            "#/definitions/Metadatas",
            "#/definitions/Polygon",
            "#/definitions/Polygons",
            "#/definitions/Tag",
            "#/definitions/Tags",
        ]:
            result = response.json()
        elif key_type == "number":
            result = response.json()
        elif key_type == "string":
            result = response.text
        else:
            result = response.json()

        return result

    def _is_uri(self, val: [str, list]):
        if isinstance(val, str):
            return val.startswith(self.server_url)
        else:
            return all([self._is_uri(v) for v in val])

    def _compute_type(self, key: str):

        schema = self.output_schema.get("properties")

        key_type = schema.get(key).get("$ref") or schema.get(key).get("type")

        return key_type
