import os

import numpy as np
import rasterio
from PIL import Image as PILImage
from pesto.ws.features.converter.image.image import Image

# os.environ['REQUESTS_CA_BUNDLE'] = '/etc/ssl/certs/ca-certificates.crt'
print('rasterio version=' + rasterio.__version__)
print('gdal version=' + rasterio.gdal_version())


def open_url(url: str):
    with rasterio.Env(GDAL_HTTP_UNSAFESSL='YES'):
        image = Image.from_uri(url).to_array()
    return image
    # try:
    #     with rasterio.open(url) as _:
    #         return _.read()
    # except:
    #     # log.debug('could not open : {}'.format(url))
    #     pass
    #
    # try:
    #     url_stream = '/vsicurl_streaming/' + url
    #     # log.debug('trying with streaming: {}'.format(url_stream))
    #     with rasterio.open(url_stream) as _:
    #         return _.read()
    # except:
    #     raise ValueError('Could not open image: {}'.format(url))


def test_sobloo_url():
    url = "https://sobloo.eu/api/v1/services/wmts/4004658d-f245-4420-8993-ebc49f80cc37/tiles/1.0.0/default/rgb/EPSG4326/8/259/64.png"
    rio_image = open_url(url)

    png_image = PILImage.open(os.path.join(os.path.dirname(__file__), "resources", "sobloo.png"))
    png_image = np.asarray(png_image)

    assert np.all(rio_image == png_image.transpose((2, 0, 1)))
