import base64
import io
import os
import numpy as np
import rasterio
from PIL import Image as PILImage
from pesto.ws.features.converter.image.image import Image as PestoImage
from pesto.ws.features.converter.image.image_roi import ImageROI

# Constants

nir_file_tif = os.path.join(os.path.dirname(__file__), "resources", "TILE_RGBN.tif")

rgb_file_tif = "/tmp/TILE_RGB.tif"
rgb_file_png = "/tmp/TILE_RGB.png"
rgb_file_jpg = "/tmp/TILE_RGB.jpg"

# Functions
def scale_chw_matrix(matrix: np.ndarray, min_percentile=1, max_percentile=99):
    try:
        c, h, w = matrix.shape
    except ValueError:
        h, w = matrix.shape
        c = 1
    matrix = matrix.reshape((c, h * w)).astype(np.float64)
    # Get 2nd and 98th percentile
    mins = np.nanpercentile(matrix, min_percentile, axis=1)
    maxs = np.nanpercentile(matrix, max_percentile, axis=1)
    matrix = (matrix - mins[:, None]) / (maxs[:, None] - mins[:, None])
    matrix = matrix.reshape((c, h, w))
    matrix = matrix.clip(0., 1.)
    return matrix


def generate_groundtruths():
    # Generate RGB 8 bits groundtruth
    with rasterio.open(nir_file_tif, "r") as dataset:
        meta = dataset.meta
        img = dataset.read()
        img = img[:3, :, :]
        img = scale_chw_matrix(img)
        img = (255. * img).astype(np.uint8)

    meta.update({"count": 3, "dtype": np.uint8})

    with rasterio.open(rgb_file_tif, "w", **meta) as dataset_rgb:
        dataset_rgb.write(img)

    pil_img = np.transpose(img, (1, 2, 0))
    pil_img = PILImage.fromarray(pil_img)
    pil_img.save(rgb_file_png, format="PNG")
    pil_img.save(rgb_file_jpg, format="JPEG")


generate_groundtruths()

# Load groundtruth
with rasterio.open(rgb_file_tif, "r") as dataset_rgb:
    img_rgb_true = dataset_rgb.read()

with rasterio.open(nir_file_tif, "r") as dataset_rgbn:
    img_rgbn_true = dataset_rgbn.read()


def test_uri_rio():
    pesto_uri_rgb = PestoImage.from_uri("file://" + rgb_file_tif).to_array()
    pesto_uri_rgbn = PestoImage.from_uri("file://" + nir_file_tif).to_array()
    pesto_uri_rgb_png = PestoImage.from_uri("file://" + rgb_file_png).to_array()

    assert np.all(img_rgbn_true == pesto_uri_rgbn)
    assert np.all(img_rgb_true == pesto_uri_rgb)
    assert np.all(img_rgb_true == pesto_uri_rgb_png)

    # Ensure that the jpg driver of rasterio produces the same result as the PIL jpg decoder
    with PILImage.open(rgb_file_jpg, mode="r") as pil_jpg:
        img_rgb_jpg_true = np.asarray(pil_jpg)
        img_rgb_jpg_true = np.transpose(img_rgb_jpg_true, (2, 0, 1))

    pesto_uri_rgb_jpg = PestoImage.from_uri("file://" + rgb_file_jpg).to_array()
    assert np.all(img_rgb_jpg_true == pesto_uri_rgb_jpg)


def test_roi_rio():
    payload = {
        "target_in": nir_file_tif,
        "target_out": nir_file_tif.replace(".tif", "_out.tif"),
        "lines": {
            "first": 128,
            "number": 128,
            "margin": 32
        },
        "columns": {
            "first": 128,
            "number": 128,
            "margin": 32
        }
    }

    roi = ImageROI(roi=payload)
    pesto_uri_rgbn = PestoImage.from_uri(uri=nir_file_tif, roi=roi).to_array()
    assert np.all(img_rgbn_true[:, (128 - 32):(128 + 128 + 32), (128 - 32):(128 + 128 + 32)] == pesto_uri_rgbn)


def test_bytes_rio():
    # Test RGB
    output_profile = dict(
        driver="GTiff",
        dtype=img_rgb_true.dtype,
        count=img_rgb_true.shape[0],
        height=img_rgb_true.shape[1],
        width=img_rgb_true.shape[2],
    )

    with rasterio.MemoryFile() as memfile:
        with memfile.open(**output_profile) as dst:
            dst.write(img_rgb_true)

        bytes_buffer = memfile.read()
        pesto_bytes_rgb = PestoImage.from_bytes(bytes_buffer).to_array()

    # Test RGBN
    output_profile = dict(
        driver="GTiff",
        dtype=img_rgbn_true.dtype,
        count=img_rgbn_true.shape[0],
        height=img_rgbn_true.shape[1],
        width=img_rgbn_true.shape[2],
    )

    with rasterio.MemoryFile() as memfile:
        with memfile.open(**output_profile) as dst:
            dst.write(img_rgbn_true)

        bytes_buffer = memfile.read()
        pesto_bytes_rgbn = PestoImage.from_bytes(bytes_buffer).to_array()

    assert np.all(img_rgb_true == pesto_bytes_rgb)
    assert np.all(img_rgbn_true == pesto_bytes_rgbn)


def test_b64_rio():
    # Test RGB
    output_profile = dict(
        driver="GTiff",
        dtype=img_rgb_true.dtype,
        count=img_rgb_true.shape[0],
        height=img_rgb_true.shape[1],
        width=img_rgb_true.shape[2],
    )

    with rasterio.MemoryFile() as memfile:
        with memfile.open(**output_profile) as dst:
            dst.write(img_rgb_true)

        bytes_buffer = memfile.read()
        bytes_b64 = base64.b64encode(bytes_buffer)
        string_b64 = bytes_b64.decode('utf-8')
        pesto_b64_rgb = PestoImage.from_base64(string_b64).to_array()

    # Test RGBN
    output_profile = dict(
        driver="GTiff",
        dtype=img_rgbn_true.dtype,
        count=img_rgbn_true.shape[0],
        height=img_rgbn_true.shape[1],
        width=img_rgbn_true.shape[2],
    )

    with rasterio.MemoryFile() as memfile:
        with memfile.open(**output_profile) as dst:
            dst.write(img_rgbn_true)

        bytes_buffer = memfile.read()
        bytes_b64 = base64.b64encode(bytes_buffer)
        string_b64 = bytes_b64.decode('utf-8')
        pesto_b64_rgbn = PestoImage.from_base64(string_b64).to_array()

    assert np.all(img_rgb_true == pesto_b64_rgb)
    assert np.all(img_rgbn_true == pesto_b64_rgbn)


def test_jpg_pil():
    pil_png = PILImage.open(rgb_file_png, mode="r")
    pil_jpg = PILImage.open(rgb_file_jpg, mode="r")
    img_rgb_jpg_true = np.asarray(pil_jpg)
    img_rgb_jpg_true = np.transpose(img_rgb_jpg_true, (2, 0, 1))

    # Test equality when sending JPG buffer from PNG image
    jpg_buffer = io.BytesIO()
    pil_png.save(jpg_buffer, format='JPEG')
    jpg_bytes = jpg_buffer.getvalue()

    pesto_bytes_jpg = PestoImage.from_bytes(jpg_bytes).to_array()

    assert (np.all(pesto_bytes_jpg == img_rgb_jpg_true))

    # Test equality when sending JPG buffer from JPG image
    png_buffer = io.BytesIO()
    pil_jpg.save(png_buffer, format='PNG')
    png_bytes = png_buffer.getvalue()

    pesto_bytes_jpg = PestoImage.from_bytes(png_bytes).to_array()

    assert (np.all(pesto_bytes_jpg == img_rgb_jpg_true))

    # Test closeness of double comrpession
    buffer = io.BytesIO()
    pil_jpg.save(buffer, format='JPEG')
    pil_bytes = buffer.getvalue()

    pesto_bytes_jpg = PestoImage.from_bytes(pil_bytes).to_array()
    pil_bytes_jpg = PILImage.open(io.BytesIO(pil_bytes))
    pil_bytes_jpg = np.asarray(pil_bytes_jpg).transpose((2, 0, 1))

    assert np.all(np.isclose(pil_bytes_jpg, pesto_bytes_jpg))


# print(np.all(img_rgbn_true == pesto_bytes_rgbn))

# Test with Base64
# buffer = BytesIO()
# image.save(buffer, 'png')
# data = base64.b64encode(buffer.getvalue())
# buffer.close()
# image_id = hashlib.sha1(image_data).hexdigest()
# return data.decode("utf-8"), image_id
