import logging
from typing import Any, Union, Optional, Tuple

import numpy as np

from pesto.ws.core.match_apply import MatchApply, Json
from pesto.ws.features.converter.image.image import Image
from pesto.ws.features.converter.image.image_roi import ImageROI

log = logging.getLogger(__name__)


class ImageConverter(MatchApply):
    URI_STRINGS = ["file://", "http://", "https://", "gs://", "s3://"]

    def __init__(self, image_roi: Optional[ImageROI]):
        self.roi = image_roi

    def match(self, schema: Json):
        ref = schema.get("$ref")
        return ref in [
            "#/definitions/Image",
            "#/definitions/Images",
        ]

    def convert(self, data: Tuple[Any, Json]):
        payload, schema = data

        if payload is None:
            return payload

        if isinstance(payload, list):
            return [self._load_image(e) for e in payload]
        return self._load_image(payload)

    def _load_image(self, image_ref: Union[str, bytes]) -> np.ndarray:
        if isinstance(image_ref, str) and any([image_ref.startswith(uri) for uri in self.URI_STRINGS]):
            image = Image.from_uri(image_ref, roi=self.roi)
            source = "uri"
        else:
            try:
                image = Image.from_bytes(image_ref)
                source = "bytes"
            except:
                image = Image.from_base64(image_ref)
                source = "base64"

        data = image.array
        log.info("loading image : {} : shape={}".format(source, data.shape))
        return data
