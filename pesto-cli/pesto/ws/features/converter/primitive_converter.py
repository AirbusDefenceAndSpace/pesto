from typing import Any, Tuple

from pesto.ws.core.match_apply import MatchApply, Json


class PrimitiveConverter(MatchApply):
    def match(self, schema: Json):
        return schema.get("type") is not None

    def convert(self, data: Tuple[Any, Json]):
        payload, schema = data
        return payload
