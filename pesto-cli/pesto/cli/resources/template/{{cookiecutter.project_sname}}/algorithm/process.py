import time
from PIL import Image
import numpy as np


def create_box(x, y, width, height):
    return {
        "type": "Polygon",
        "coordinates": [[[x, y], [x, y + height], [x + width, y + height], [x + width, y], [x, y]]],
    }


class Process:
    """
    Custom processing class
    """
    MODEL = None

    # Do not call __init__

    def on_start(self) -> None:
        """
        Process.on_start will be called at server start time.
        If you need to load heavy resources before processing data, this should be done here.
        """
        def my_model(image: np.ndarray, gamma: float):
            # Image is parsed as (C, H, W) - rasterio convention, so we put it back to (H, W C)
            img = np.transpose(image, (1, 2, 0))

            # A dummy model that modifies gamma
            img = img.astype(np.float32) / 255.0
            img = img**gamma
            img = np.clip(img, 0.0, 1.0)

            img = (255.0 * img).astype(np.uint8)

            # Put image back to (H, W, C) format for response parsing
            img = np.transpose(img, (2, 0, 1))

            return img

        Process.MODEL = staticmethod(my_model)

    # process function, called each time a processing request is send to the service.
    # note: images are represented in numpy as follows [channel, hight, width].
    def process(
        self,
        image,
        dict_parameter,
        object_parameter,
        integer_parameter,
        number_parameter,
        string_parameter,
    ):
        """
        The core algorithm is implemented here.
        """

        # Defaults
        dict_parameter = dict_parameter or dict()
        object_parameter = object_parameter or dict()
        integer_parameter = integer_parameter or 0
        number_parameter = number_parameter or 0.7
        string_parameter = string_parameter or "defaultString"

        dict_parameter["object"] = object_parameter

        # Simulates longer algorithm
        time.sleep(5)

        h, w = image.shape[1], image.shape[2]

        # Apply a model
        output = self.MODEL(image=image, gamma=number_parameter)

        # Create a list of polygons for demo purposes
        areas = [
            create_box(0, 0, width=w, height=h),
            create_box(int(w // 4), int(h // 4), width=int(w // 2), height=int(h // 2)),
        ]

        # Create a list of image for demo purposes
        image_list = [
            self.MODEL(image=image, gamma=0.7),
            self.MODEL(image=image, gamma=1.5),
        ]

        result = {
            "image": output,
            "number_output": number_parameter,
            "integer_output": integer_parameter,
            "string_output": string_parameter,
            "dict_output": dict_parameter,
            "areas": areas,
            "image_list": image_list,
            "geojson": {
                "features": [
                    {
                        "geometry": create_box(0, 0, width=w, height=h),
                        "properties": {
                            "category": "cat",
                            "confidence": 0.99,
                            "name": "chelsea"
                        },
                        "type": "Feature",
                    },
                    {
                        "geometry": create_box(int(w // 4), int(h // 4), width=int(w // 2), height=int(h // 2)),
                        "properties": {
                            "category": "egyptian_cat",
                            "confidence": 0.42,
                        },
                        "type": "Feature",
                    },
                ]
            },
        }

        return result
