from typing import Callable, Any, Tuple

from pesto.ws.core.match_apply import MatchApply, Json


class ObjectConverter(MatchApply):
    def __init__(self, convert: Callable):
        self.delegate = convert

    def match(self, schema: Json):
        return schema.get("type") == "object"

    def convert(self, data: Tuple[Any, Json]):
        payload, schema = data
        if payload is None:
            return payload

        return {
            key: self.delegate(e, schema["properties"][key])
            for key, e in payload.items() if key in schema["properties"]
        }
