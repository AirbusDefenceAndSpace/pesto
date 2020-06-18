import base64
import logging
import os
from typing import Optional

import numpy as np
import rasterio
from pesto.ws.features.converter.image.image_driver import ImageDriver
from pesto.ws.features.converter.image.image_roi import ImageROI

log = logging.getLogger(__name__)

# disable rasterio logs
_rasterio_log = rasterio.logging.getLogger()
_rasterio_log.setLevel(rasterio.logging.ERROR)


class Image:
    @staticmethod
    def from_array(array: np.ndarray) -> 'Image':
        img = Image(array)
        return img

    def to_array(self):
        return self.array

    @staticmethod
    def from_bytes(image_bytes: bytes) -> 'Image':
        with rasterio.MemoryFile(image_bytes) as memory_file:
            with memory_file.open() as file:
                array = file.read()
                return Image.from_array(array=array)

    def to_bytes(self) -> bytes:
        driver = ImageDriver.TIFF if self.bands() > 3 else ImageDriver.PNG

        output_profile = dict(
            driver=driver.driver,
            width=self.width(),
            height=self.height(),
            count=self.bands(),
            dtype=self.array.dtype,
        )

        with rasterio.MemoryFile() as memfile:
            with memfile.open(**output_profile) as dst:
                dst.write(self.array)

            buffer = memfile.read()

        return buffer

    @staticmethod
    def from_uri(uri: str, roi: Optional[ImageROI] = None) -> 'Image':
        try:
            log.debug('opening with rasterio: {}'.format(uri))
            with rasterio.open(uri) as _:
                return _load_image(_, roi)
        except:
            streaming_url = '/vsicurl_streaming/' + uri
            log.debug('trying with streaming: {}'.format(streaming_url))
            with rasterio.open(streaming_url) as _:
                return _load_image(_, roi)

    def to_path(self, path: str) -> str:
        driver = ImageDriver.match_path(path) or ImageDriver.TIFF

        path = os.path.splitext(path)[0] + driver.ext
        os.makedirs(os.path.dirname(path), exist_ok=True)
        log.info('save image [{}]: {} dtype={} to {}'.format(driver, self.array.shape, self.array.dtype, path))
        copy = self.array.astype(np.uint8)
        with rasterio.open(path,
                           mode='w',
                           driver=driver.driver,
                           width=self.width(),
                           height=self.height(),
                           count=self.bands(),
                           dtype=copy.dtype) as output:
            output.write(copy)
        return path

    @staticmethod
    def from_base64(string_b64: str) -> 'Image':
        bytes_b64 = string_b64.encode('utf-8')
        raw_bytes = base64.b64decode(bytes_b64)
        return Image.from_bytes(raw_bytes)

    def to_base64(self) -> str:
        raw_bytes = self.to_bytes()
        bytes_b64 = base64.b64encode(raw_bytes)
        string_b64 = bytes_b64.decode('utf-8')
        return string_b64

    def __init__(self, array: np.ndarray = None):
        if array.ndim == 2:
            array = np.expand_dims(array, 0)
        self.array = array
        log.info('new image : {} dtype={}'.format(self.array.shape, self.array.dtype))

    def width(self) -> int:
        return self.array.shape[2]

    def height(self) -> int:
        return self.array.shape[1]

    def bands(self) -> int:
        return self.array.shape[0]


def _load_image(dataset, roi: Optional[ImageROI]):
    if roi is None:
        data = dataset.read()
    else:
        lines, columns = dataset.shape
        y0, yn, ym = roi.lines.first, roi.lines.number, roi.lines.margin
        x0, xn, xm = roi.columns.first, roi.columns.number, roi.columns.margin
        top, bottom = max(0, y0 - ym), min(lines, y0 + yn + ym)
        left, right = max(0, x0 - xm), min(columns, x0 + xn + xm)
        data = dataset.read(window=((top, bottom), (left, right)))
    return Image.from_array(data)
