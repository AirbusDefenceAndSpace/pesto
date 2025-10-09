from typing import Optional

import jsonschema
from pesto.common.testing import logger
from pesto.common.testing.endpoint_manager import EndpointManager
from pesto.common.utils import compare_dicts


class ServiceTester:
    def __init__(self, server_url):
        self.server_url = server_url
        self.endpoint_manager = EndpointManager(self.server_url)

    def validate_health(self):
        return self.endpoint_manager.is_alive

    # Walk recursively the dict in order to substitute "http://localhost:4000" with actual base URL in the value of key "href"
    def update_hrefs(self, data):
        if isinstance(data, dict):
            for key, value in data.items():
                if key == "href" and isinstance(value, str):
                    data[key] = value.replace("http://localhost:4000", self.server_url)
                else:
                    self.update_hrefs(value)
        elif isinstance(data, list):
            for item in data:
                self.update_hrefs(item)

    def validate_metrics(self):
        return self.endpoint_manager.metrics_available

    def validate_describe(self, expected_describe: dict):
        describe = self.endpoint_manager.describe
        expected = expected_describe

        # normalize expected data
        self.update_hrefs(expected)

        # We can afford new keys in the describe
        # as it reflect a newer runtime (new endpoints) than the stored reference.
        comparison_results = compare_dicts(expected, describe, allow_unexpected_keys=True)

        comparison_results = comparison_results or {"NoDifference": True}

        return comparison_results

    def validate_process(self, payload: dict, expected_response: Optional[dict]):

        validation_result = dict()

        logger.info("Validating payload against input schema")
        try:
            jsonschema.validate(payload, self.endpoint_manager.input_schema)
        except jsonschema.ValidationError as e:
            print(e)
            validation_result["input_schema"] = False
            return "NO RESPONSE", validation_result
        except jsonschema.SchemaError as e:
            print(e)
            validation_result["input_schema"] = False
            return "NO RESPONSE", validation_result

        logger.info("Validation OK")
        validation_result["input_schema"] = True

        logger.info("Computing response")
        response = self.endpoint_manager.process(payload)

        logger.info("Validating response against output schema")
        try:
            jsonschema.validate(payload, self.endpoint_manager.input_schema)
        except jsonschema.ValidationError as e:
            logger.error(e)
            validation_result["output_schema"] = False
        except jsonschema.SchemaError as e:
            logger.error(e)
            validation_result["output_schema"] = False

        logger.info("Validation OK")
        validation_result["output_schema"] = True
        expected_response = expected_response or dict()

        validation_result = compare_dicts(expected_response, response)

        validation_result = validation_result or {"NoDifference": True}

        return response, validation_result
