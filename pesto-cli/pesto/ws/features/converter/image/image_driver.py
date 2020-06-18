import logging
import os
from enum import Enum

log = logging.getLogger(__name__)


class ImageDriver(Enum):
    TIFF = ('.tif', 'GTiff')
    PNG = ('.png', 'PNG')
    JPG = ('.jpg', 'JPEG')

    @staticmethod
    def match_path(path: str):
        _, ext = os.path.splitext(path)
        ext = ext.replace('.', '')

        if ext in ['jpeg', 'jpg']:
            return ImageDriver.JPG
        elif ext in ['tif', 'tiff']:
            return ImageDriver.TIFF
        elif ext in ['png']:
            return ImageDriver.PNG
        else:
            log.error('image : unsupported extension : {}'.format(ext))
            return None

    @property
    def ext(self) -> str:
        return self.value[0]

    @property
    def driver(self) -> str:
        return self.value[1]
