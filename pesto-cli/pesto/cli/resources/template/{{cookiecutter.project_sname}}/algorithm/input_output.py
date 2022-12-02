from dataclasses import dataclass
from pesto.cli.fields import Definition, field, definition
import numpy as np
from typing import List

@dataclass
class Input:
    image:np.array = definition(type=Definition.Image, required=True, description="The input image")
    dict_parameter:dict = definition(type=Definition.Metadata, description="Some metadata parameters")
    integer_parameter: int = field("Some integer value")
    number_parameter: float = field(required=True, description="One float")
    string_parameter: str = field(description="One string")
    undocumented_parameter: str = "" 
    
@dataclass
class Output:
    image:np.array = definition(Definition.Image, description="The output image")
    number_output: float = field(required=False, description="One float")
    integer_output: int = field(required=True, description="One integer")
    string_output: str = field(required=False, description="One string")
    dict_output: dict = definition(Definition.Metadata, required=True, description="One metadata")
    areas: object = definition(Definition.Polygons, required=True, description="One Polygon")
    image_list: List[np.array] = definition(Definition.Images, description="The output images")
    
    # Add your own definition in 
#    geojson: object = definition("#/definitions/GeoJSON", description="The output geojson")
