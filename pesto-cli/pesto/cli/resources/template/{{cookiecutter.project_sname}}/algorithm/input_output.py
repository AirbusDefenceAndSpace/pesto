from dataclasses import dataclass
from pesto.cli.fields import Definition, field, definition
import numpy as np
from typing import List

@dataclass
class Input:
    image:np.array = definition(type=Definition.Image, required=True, description="Input image")
    dict_parameter:dict = definition(type=Definition.Metadata, description="A dict parameter")
    object_parameter:object = definition(type=Definition.Metadata, description="A dict parameter with more spec, of the form {'key':'value'}")
    integer_parameter: int = field("A (integer) number parameter")
    number_parameter: float = field(description="A (floating point) number parameter")
    string_parameter: str = field(description="A string parameter")
    
@dataclass
class Output:
    image:np.array = definition(Definition.Image, description="The output image")
    areas: object = definition(Definition.Polygons, description="One Polygon")
    number_output: float = field()
    integer_output: int = field()
    dict_parameter:dict = definition(type=Definition.Metadata, description="A dict parameter")
    dict_output: dict = definition(Definition.Metadata)
    string_output:str = field()
    image_list: List[np.array] = definition(Definition.Images, description="The output images")
    geojson:object = definition(Definition.Metadata)
