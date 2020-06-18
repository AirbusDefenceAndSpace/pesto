from pesto.ws.features.serializer.image_serializer import ImageSerializer
import numpy as np


def test_image_serializer():
    array = (np.random.random((3, 100, 100)) * 255).astype(np.uint8)
    data = (array, 'test_image')
    ImageSerializer('/tmp/pesto/TU/', None).convert(data)
