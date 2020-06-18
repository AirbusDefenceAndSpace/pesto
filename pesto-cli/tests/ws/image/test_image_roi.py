import os
from pesto.ws.features.converter.image.image import Image
from pesto.ws.features.converter.image.image_roi import ImageROI


def create_payload(image_path: str):
    return {
        'img1': image_path,
        'img2': image_path,
        "pesto": {
            "roi": {
                "target_in": ['img1', 'img2'],
                "target_out": ['img1', 'img2'],
                "lines": {
                    "first": 10,
                    "number": 20,
                    "margin": 20
                },
                "columns": {
                    "first": 190,
                    "number": 56,
                    "margin": 50
                }
            }
        }
    }


def test_roi():
    payload = create_payload(os.path.join(os.path.dirname(__file__), 'resources/img_256x128.jpg'))

    pesto = payload.pop('pesto')
    roi_conf = pesto.pop('roi')
    roi = ImageROI(roi_conf)

    payload = roi.compute_crop_infos().process(payload)

    # load images with cropping
    for _ in roi.target_in:
        payload[_] = Image.from_uri(payload[_], roi).array
        shape = payload[_].shape
        assert shape == (3, 50, 116)

    # remove margins
    payload = roi.remove_margin().process(payload)

    for _ in roi.target_out:
        shape = payload[_].shape
        assert shape == (3, roi.lines.number, roi.columns.number)
