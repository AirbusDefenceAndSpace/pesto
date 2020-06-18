import logging
from typing import Dict, Any

from pesto.ws.core.match_apply import MatchPipeline
from pesto.ws.features.converter.array_converter import ArrayConverter
from pesto.ws.features.converter.image.image_roi import ImageROI
from pesto.ws.features.converter.image_converter import ImageConverter
from pesto.ws.features.converter.metadata_converter import MetadataConverter
from pesto.ws.features.converter.object_converter import ObjectConverter
from pesto.ws.features.converter.primitive_converter import PrimitiveConverter
from pesto.ws.core.pesto_feature import PestoFeature

log = logging.getLogger(__name__)


class PayloadConverter(PestoFeature):
    def __init__(self, image_roi: ImageROI, schema: dict):
        self.schema = schema

        self.input_convert = MatchPipeline([
            ImageConverter(image_roi),
            MetadataConverter(),
            ObjectConverter(self._convert),
            ArrayConverter(self._convert),
            PrimitiveConverter()
        ])

    def process(self, payload: dict) -> dict:
        log.info('payload : '.format(str(payload)))
        return {
            key: self._convert(payload.get(key, None), schema)
            for key, schema in self.schema['properties'].items()
        }

    def _convert(self, value: Any, schema: Dict):
        return self.input_convert.convert((value, schema), schema)
