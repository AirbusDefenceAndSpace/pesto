from abc import ABC
from typing import Dict, Any, List

Json = Dict[str, Any]


class MatchApply(ABC):
    def match(self, schema: Json):
        raise NotImplementedError()

    def convert(self, data: Any):
        raise NotImplementedError()


class MatchPipeline:
    def __init__(self, pipeline: List[MatchApply], default: MatchApply = None):
        self.pipeline = pipeline
        self.default = default

    def convert(self, value: Any, schema: Dict):
        for _ in self.pipeline:
            if _.match(schema):
                return _.convert(value)

        if self.default is None:
            raise ValueError('Unsupported data type {} : value={}'.format(schema, str(value)))

        return self.default.convert(value)
