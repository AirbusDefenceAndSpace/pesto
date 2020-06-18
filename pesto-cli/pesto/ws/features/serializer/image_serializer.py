import logging
import os
from typing import Tuple, Any, Dict

import numpy as np
from pesto.ws.core.match_apply import MatchApply, Json
from pesto.ws.features.converter.image.image import Image

log = logging.getLogger(__name__)


class ImageSerializer(MatchApply):
    def __init__(self, job_path: str, schema: Dict):
        self.job_path = job_path
        try:
            output_content = schema["content"]["content"]
            self._default_driver = output_content.replace("image/", "")
        except:
            self._default_driver = "png"

    def match(self, schema: Json):
        ref = schema.get("$ref")
        return ref in [
            "#/definitions/Image",
            "#/definitions/Images",
        ]

    def convert(self, data: Tuple[Any, str]):
        payload, key = data
        if isinstance(payload, list):
            for index, array in enumerate(payload):
                self._save_image(array, key + str(index))
            return
        array = payload
        self._save_image(array, key)

    def _save_image(self, array: np.ndarray, key: str) -> None:
        image = Image(array=array)

        if image.bands() > 4:
            driver = "tif"
        else:
            driver = self._default_driver

        filename = os.path.join(self.job_path, "{}.{}".format(key, driver))
        log.info("saving image : " + filename)
        image.to_path(filename)
