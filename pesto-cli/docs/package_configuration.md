# Configuration of your PESTO web service

In your PESTO project, the following file have to be edited to describe your custom algorithm.

```
algorithm/
└── process.py
pesto/api/
├── config.json
├── config_schema.json
├── description.json
├── input_schema.json
├── output_schema.json
└── version.json
```

PESTO configuration is done in three steps :

1. Define the API
    - pesto/api/input_schema.json : json schema describing the input payloads,
    - pesto/api/output_schema.json : json schema describing the output payloads, 

2. Implement your process
    - algorithm/process.py : implementation of the processing and its entry point

3. Package
    - pesto/api/description.json : informative description of the algorithm including deployment requirements
    - pesto/build/requirements.json : required files and library (your model is defined here) to build the web service.

!!! tip

    Always start from the [pesto-template](pesto_init.md) as it is already a working PESTO project.



## Input / Output specification

The first thing to do is define the processing input and output.
The REST API use json to communicate with external services or users.
We then use [JSON schema](https://json-schema.org/) to validate input payloads. 

`pesto/api/input_schema.json` : specify the input validation schema

!!! example "Example: input_schema.json"
    ```json
    {
      "image": {
        "$ref": "#/definitions/Image",
        "description": "Input image"
      },
      "dict_parameter": {
        "$ref": "#/definitions/Metadata",
        "description": "A dict parameter"
      },
      "object_parameter": {
        "description": "A dict parameter with more spec, of the form {'key':'value'}",
        "type": "object",
        "properties": {
          "key": {
            "type": "string"
          }
        }
      },
      "number_parameter": {
        "type": "number",
        "description": "A (floating point) number parameter"
      },
      "integer_parameter": {
        "type": "integer",
        "description": "A (integer) number parameter"
      },
      "string_parameter": {
        "type": "string",
        "description": "A string parameter"
      },
      "required": [
        "image"
      ]
    }
    ```

`pesto/api/output_schema.json` : specify the output validation schema.


!!! example "Example: output_schema.json"
    ```json
    {
      "image": {
        "$ref": "#/definitions/Image"
      },
      "areas": {
        "$ref": "#/definitions/Polygons"
      },
      "number_output": {
        "type": "number"
      },
      "integer_output": {
        "type": "integer"
      },
      "dict_output": {
        "$ref": "#/definitions/Metadata"
      },
      "string_output": {
        "type": "string"
      },
      "image_list": {
        "$ref": "#/definitions/Images"
      },
      "geojson": {
        "description": "A Geojson.FeatureCollection containing only Polygons as geometries",
        "type": "object",
        "properties": {
          "features": {
            "type": "array",
            "items": {
              "$schema": "http://json-schema.org/draft-06/schema#",
              "title": "GeoJSON Feature",
              "type": "object",
              "required": [
                "type",
                "properties",
                "geometry"
              ],
              "properties": {
                "type": {
                  "type": "string",
                  "enum": [
                    "Feature"
                  ]
                },
                "properties": {
                  "oneOf": [
                    {
                      "type": "null"
                    },
                    {
                      "type": "object"
                    }
                  ]
                },
                "geometry": {
                  "$ref": "#/definitions/Polygon"
                }
              }
            }
          },
          "type": {
            "type": "string"
          }
        }
      }
    }
    ```

The `json` files contain the input/output variables name and their information (`type`/`$ref`, `description`)


Default PESTO types can be found in the source code : `processing-factory/pesto-cli/pesto/cli/resources/schema/definitions.json`


There are two ways to specify these schemas.

* **Solution 1**: Pesto schema generator

The `schemagen` command is based on two python classes used to declare input and output.
These classes are detailed in [pesto schemagen command](pesto_schemagen.md).
Once they are properly configured, just run schemagen command to generated python files
```bash
$ pesto schemagen
```

* **Solution 2**: Direct json

The `pesto/api/input_schema.json` and `pesto/api/output_schema.json` can be directly configured to describe input and output


## Python algorithm

The `algorithm/process.py` should contains a `Process` class with the `Process.process()` method.

!!! note
    Images are converted to/from numpy arrays by PESTO. Thus, the `Process.process()` method should expect to receive **numpy arrays** and always return images as **numpy arrays**.

```python
class Process(object):
    def process(self, image, dict_parameter):
        # do some processing on the input
        return {
            'partial_result_1': {},
            'partial_result_2': {},
            'confidence': 1.0
        }
```

!!! warning
    Be sure to match the `input_schema.json` and `output_schema.json` in the `Process.process()` method arguments and result.


## Requirements

PESTO provides a generic way to include any files in the final docker image using the `pesto/build/requirements.json` file.

The following fields are required :

- **environments**: some user defined variables
- **requirements**: A (from,to) list, where `from` is an URI to some files and `to` is the target path in the docker image
- **dockerBaseImage** : the docker image to use as a base

!!! example "Example: requirements.json"
```json
{
  "environments": {
    "DEEPWORK": "/deep/deliveries",
    "DEEPDELIVERY": "/deep/deliveries"
  },
  "requirements": {
    "lib1": {
      "from": "file:///tmp/my-lib1.tar.gz",
      "to": "/opt/lib1",
      "type": "python"
    },
    "lib2": {
      "from": "file:///tmp/my-lib2.tar.gz",
      "to": "/opt/lib2",
      "type": "pip"
    },
    "model": {
      "from": "gs://path/to/my-model.tar.gz",
      "to": "/opt/model"
    }
  },
  "dockerBaseImage": "python:3.8-buster"
}
```


PESTO can handle requirements in many formats. Each requirement accepts an optional `type` field :

- *python* : add the `to` path to the PYTHONPATH environment variable
- *pip* : run a `pip install` command on the provided `wheel` or setuptools compatible `tar.gz` archive
- *default* : simply copy the files (uncompressed the `tar.gz` archive)

!!! warning 

    The tar.gz with type 'python' usage is DEPRECATED and will fail with an archive build with setuptools.
    Such an archive contains a root folder that should be removed when adding the path to PYTHON_PATH.



