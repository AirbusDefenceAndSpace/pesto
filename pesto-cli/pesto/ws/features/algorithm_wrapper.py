from typing import Any
import inspect
import logging
from pesto.ws.core.utils import load_class

from pesto.ws.core.pesto_feature import PestoFeature

log = logging.getLogger(__name__)


class AlgorithmWrapper(PestoFeature):

    def __init__(self, algorithm: Any, input_class):
        self.algorithm = algorithm
        self.input_class=input_class

    def process(self, payload: dict) -> dict:
        params = list(inspect.signature(self.algorithm.process).parameters.values())
        if len(params)==1 and params[0].annotation and params[0].annotation == self.input_class: 
            log.info("Provide the parameters in one input object")
            payload = self.algorithm.process(self.input_class(**payload))
        else:
            log.info("Provide directly the parameters")
            payload = self.algorithm.process(**payload)
        return payload
