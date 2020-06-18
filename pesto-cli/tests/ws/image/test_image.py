import os
import numpy as np

from pesto.ws.features.converter.image.image import Image
from pesto.ws.features.converter.image.image_roi import ImageROI


def get_image():
    return (np.random.random((3, 20, 20)) * 255.).astype(np.uint8)


def test_image_bytes_conversion():
    data = get_image()

    img = Image.from_array(data)
    img_bytes = img.to_bytes()
    img_back = Image.from_bytes(img_bytes)
    data_back = img_back.array
    data = np.moveaxis(data, 0, -1)
    data_back = np.moveaxis(data_back, 0, -1)

    assert np.array_equal(data.shape, data_back.shape)
    # assert np.array_equal(data, data_back)


def test_image_roi():
    data = os.path.abspath(os.path.join(os.path.dirname(__file__), 'resources/img_256x128.jpg'))
    data = "file://" + data

    roi = ImageROI({
        "target_in": data,
        "target_out": data,
        'lines': {
            'first': 0,
            'number': 100,
            'margin': 10
        },
        'columns': {
            'first': 0,
            'number': 200,
            'margin': 15
        }
    })
    img_full = Image.from_uri(data).array
    img = Image.from_uri(data, roi).array
    assert (img.shape[0] == img_full.shape[0])
