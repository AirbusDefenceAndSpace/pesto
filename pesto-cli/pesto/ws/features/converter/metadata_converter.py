from typing import Any, Tuple

from pesto.ws.core.match_apply import MatchApply, Json


class MetadataConverter(MatchApply):
    def match(self, schema: Json):
        ref = schema.get('$ref')
        return ref in [
            '#/definitions/Metadata',
            '#/definitions/Metadatas',
        ]

    def convert(self, data: Tuple[Any, Json]):
        payload, schema = data
        return payload
