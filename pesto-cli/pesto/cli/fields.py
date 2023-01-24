from enum import Enum, auto
import numpy as np
from typing import Dict, List
import dataclasses


class Definition(Enum):
    Image = auto()
    Images = auto()
    Polygon = auto()
    Polygons = auto()
    Metadata = auto()
    Metadatas = auto()


NATIVES = {str: "string", int: "integer", float: "number"}


class Param:
    type = "pesto.type"
    description = "pesto.description"
    required = "pesto.required"


def field(description: str = "", required: bool = False, **kwargs):
    return dataclasses.field(
        metadata={Param.description: description, Param.required: required}, **kwargs
    )


def definition(
    definition: Definition, description: str = "", required: bool = False, **kwargs
):
    return dataclasses.field(
        metadata={
            Param.type: definition,
            Param.description: description,
            Param.required: required,
        },
        **kwargs
    )


def user_definition(
    definition: str, description: str = "", required: bool = False, **kwargs
):
    return dataclasses.field(
        metadata={
            Param.type: definition,
            Param.description: description,
            Param.required: required,
        },
        **kwargs
    )
