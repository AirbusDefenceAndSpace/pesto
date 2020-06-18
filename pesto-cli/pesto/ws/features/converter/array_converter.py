from typing import Callable, Any, Tuple

from pesto.ws.core.match_apply import MatchApply, Json


class ArrayConverter(MatchApply):

    def __init__(self, convert: Callable):
        self.delegate = convert

    def match(self, schema: Json):
        return schema.get('type') == 'array'

    def convert(self, data: Tuple[Any, Json]):
        payload, schema = data
        if payload is None:
            return payload
        return [self.delegate(e, schema['items']) for e in payload]
