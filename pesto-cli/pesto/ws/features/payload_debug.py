import logging

from pesto.ws.core.pesto_feature import PestoFeature

log = logging.getLogger(__name__)


class PayloadDebug(PestoFeature):
    def __init__(self, schema: dict):
        self.schema = schema

    def process(self, payload: dict) -> dict:
        log.info('listing inputs')
        for key, value in self.schema['properties'].items():
            key_type = value.get('$ref', value)
            try:
                key_infos = payload[key].shape
            except:
                key_infos = 'json'
            log.info('{} : {} : {}'.format(key, key_type, key_infos))
        return payload
