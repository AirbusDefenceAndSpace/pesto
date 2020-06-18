import logging
import os
import shutil
from typing import Any

from pesto.ws.features.converter.image.image import Image
from pesto.ws.core.pesto_feature import PestoFeature
from pesto.ws.service.job_list import JobListService
from pesto.ws.service.job_result import JobResultService, ResultType

log = logging.getLogger(__name__)


class StatelessResponse(PestoFeature):
    def __init__(self, url_root: str, job_id: str, schema: dict):
        self.result_service = JobResultService(url_root, job_id)
        self.url_root = url_root
        self.job_id = job_id
        self.schema = schema
        self.output_properties = self.schema['properties']

    def process(self, payload: dict) -> Any:
        try:
            if self._unique_response():
                log.info('response mode : stateless : unique response')
                result_id = list(self.schema.keys())[0]
                path, data_type = self.result_service.get_partial_result(result_id)
                if data_type == ResultType.image:
                    return path, ResultType.image

            log.info('response mode : stateless')
            for key in payload.keys():
                key_type = self.output_properties[key].get('$ref')
                if key_type == '#/definitions/Image':
                    payload[key] = Image.from_array(payload[key]).to_base64()
                elif key_type == '#/definitions/Images':
                    for index, img in enumerate(payload[key]):
                        payload[key][index] = Image.from_array(payload[key][index]).to_base64()
            return payload, ResultType.json
        finally:
            job_path = os.path.join(JobListService.PESTO_WORKSPACE, self.job_id)
            shutil.rmtree(job_path, ignore_errors=True)

    def _unique_response(self) -> bool:
        log.info('output_properties: {}'.format(str(self.output_properties)))

        try:
            unique_response = len(set(self.output_properties)) == 1
            key_type = self.output_properties[0].get('$ref')
            is_dict = key_type in ['#/definitions/Metadata',
                                   '#/definitions/Metadatas',
                                   '#/definitions/Polygon',
                                   '#/definitions/Polygons'
                                   ]

            return unique_response and is_dict
        except:
            return False
