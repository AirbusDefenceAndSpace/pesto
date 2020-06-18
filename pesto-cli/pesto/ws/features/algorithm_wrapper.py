from typing import Any

from pesto.ws.core.pesto_feature import PestoFeature


class AlgorithmWrapper(PestoFeature):
    def __init__(self, algorithm: Any):
        self.algorithm = algorithm

    def process(self, payload: dict) -> dict:
        payload = self.algorithm.process(**payload)
        return payload
