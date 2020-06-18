import logging
import os

from pesto.ws.core.match_apply import MatchPipeline
from pesto.ws.core.pesto_feature import PestoFeature
from pesto.ws.features.serializer.image_serializer import ImageSerializer
from pesto.ws.features.serializer.json_serializer import JsonSerializer
from pesto.ws.features.serializer.number_serializer import NumberSerializer
from pesto.ws.features.serializer.string_serializer import StringSerializer
from pesto.ws.service.job_list import JobListService

log = logging.getLogger(__name__)


class ResponseSerializer(PestoFeature):

    def __init__(self, schema: dict, job_id: str):
        self.schema = schema

        job_path = os.path.join(JobListService.PESTO_WORKSPACE, job_id)
        self.output_serialize = MatchPipeline([
            ImageSerializer(job_path, schema=schema),
            JsonSerializer(job_path),
            NumberSerializer(job_path),
            StringSerializer(job_path)
        ], default=JsonSerializer(job_path))

    def process(self, payload: dict) -> dict:
        log.info('saving response to disk ...')

        for key, schema in self.schema['properties'].items():
            ref = schema.get('$ref')
            key_type = schema.get('type')

            log.info('saving {}: $ref={} type={}'.format(key, ref, key_type))
            if payload.get(key) is not None:
                self.output_serialize.convert((payload.get(key), key), schema)

        log.info('response saved !')
        return payload
