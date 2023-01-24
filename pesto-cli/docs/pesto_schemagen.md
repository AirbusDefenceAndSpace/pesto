# `pesto schemagen` : Generate the input/output schemas

PESTO's webservice needs the `pesto/api/input_schema.json` and `pesto/api/output_schema.json` files to specify the input and output formats of the algorithm. The schemas must match with the `Process.process()` function signature. It can be laborious to specify valid schemas that are perfectly aligned with the function signature. The `schemagen` action of `pesto` generates the input and output schemas for you.

To generate the `pesto/api/input_schema.json` and `pesto/api/output_schema.json` files, simply run:
```shell
pesto schemagen /path/to/your/workspace/xxx-service
```
!!! Success
    ```shell
    ...
    The Input schema is now in algo-service/pesto/api/input_schema.json
    The Output schema is now in algo-service/pesto/api/output_schema.json
    ```

The input and output files contain the schemas:

!!! Example "Input and output schemas"
    === "Input schema"
        ```json linenums="1" title="input_schema.json"
        {
            "image": {
                "$ref": "#/definitions/Image",
                "description": "Input image"
            },
            ...
            "string_parameter": {
                "type": "string",
                "description": "A string parameter"
            },
            "required": [
                "image"
            ]
        }
        ```

    === "Output schema"
        ```json linenums="1" title="output_schema.json"
        {
            "image": {
                "$ref": "#/definitions/Image"
            },
            "areas": {
                "$ref": "#/definitions/Polygons"
            },
            ...
            "image_list": {
                "$ref": "#/definitions/Images"
            }
        }
        ```


!!! Important
    - Remember to run `pesto schemagen` every time you change `algorithm/input_output.py`
    - The input and output files are left intact if already existing. Use `--force` to overwrite the files.

Remember to run `schemagen --force` every time you change your files so that the function's signature and the schemas are synched.
```shell
pesto schemagen --force /path/to/your/workspace/xxx-service
```

## Input and Output dataclasses

To benefit from the `schemagen` action, you need to :

- encapsulated the input parameters in the `Input` class
- encapsulate the return objects in the `Output` class
- use the `process(input: Input) -> Output` signature

The `Input` and `Output` class must be python [dataclasses](https://docs.python.org/3/library/dataclasses.html):

```python linenums="1" title="input_output.py"
from dataclasses import dataclass
from pesto.cli.fields import Definition, field, definition, user_definition
import numpy as np
from typing import List

@dataclass
class Input:
    image:np.array = definition(Definition.Image, required=True, description="Input image")
    dict_parameter:dict = definition(Definition.Metadata, description="A dict parameter")
    integer_parameter: int = field("A (integer) number parameter")
    ...

@dataclass
class Output:
    integer_output: int
    string_output:str = field()
    image_list: List[np.array] = definition(Definition.Images, description="The output images")
    geojson:object = user_definition("geojson")
    ...
```

Each field has its schema inferred from it's python type or definition.

## JSON Schema inference

### From a python type

A typed field is enough to infer the json schema. Supported python types are

- `str` : mapped to a json string field
- `int` : mapped to a json integer field
- `float` : mapped to a json number field

Example:
```python linenums="1" title="input_output.py"
@dataclass
class Input:
    integer_output: int
    string_output:str
```

To attach documentation, simply use the `field()` function. This description will go to the json schema.
```python linenums="1" title="input_output.py"
@dataclass
class Input:
    integer_parameter: int = field("An integer parameter")
```

### From a PESTO Definitions

PESTO definitions are standard reusable structures.

Supported PESTO Definitions are:

- `Image` : a [numpy array](details_conventions.md#image-format-numpy-array)
- `Images` : a list of `Image`
- `Polygon` : a geojson `Polygon` geometry
- `Polygons` : a list of `Polygon`
- `Metadata` : a generic json object
- `Metadatas` : a list of `Metadata`

Example for defining an image field with its description:
```python linenums="1" title="input_output.py"
@dataclass
class Input:
    image:np.array = definition(Definition.Image, description="The output image")
```

### From a user defined Definitions

You also can define your own definitions and use them in the `input_output.py` file. 

Add your definition in the `api/user_definitions.json` file:
```json linenums="1" title="api/user_definitions.json"
{
    "object_parameter": {
        "description": "A dict parameter with more spec, of the form {'key':'value'}",
        "type": "object",
        "properties": {
            "key": {
                "type": "string"
            }
        }
    }
}
```

Then use the definition in `input_output.py` :
```python linenums="1" title="input_output.py"
@dataclass
class Output:
    geojson:object = user_definition("object_parameter")
```


## `Schemagen` checklist
!!! tip "Checklist"
    In order to make sure that schemagen can generate the input and output schema files, remember the following rules:

    - The algorithm signature is `process(input: Input) -> Output`
    - The `Input` and `Output` classes are annotated with `@dataclass` (they are therefore python dataclasses)
    - The input_output.py class is a correct python file
    - if you generate the schemas, remember to use `--force` to overwrite the existing files
