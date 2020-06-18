import logging
from abc import ABC
from typing import List

log = logging.getLogger(__name__)


class PestoFeature(ABC):
    def process(self, payload: dict) -> dict:
        raise NotImplementedError()


class PestoFeatures(PestoFeature):
    def __init__(self, features: List[PestoFeature]):
        self.features = features

    def process(self, payload: dict) -> dict:
        result = payload
        for feat in self.features:
            log.info('PESTO PROCESSING : [{}]'.format(feat.__class__.__name__))
            result = feat.process(result)
        return result
