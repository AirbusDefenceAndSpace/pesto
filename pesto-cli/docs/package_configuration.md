# Configuring the PESTO packaging of your algorithm

Once you [initialized](pesto_init.md) the new PESTO project, a number of files has to be edited to describe the algorithm's input, output and requirements.

??? abstract "List of configuration files"

    | File      | Description                          |
    | :---------- | :---------------------- |
    | `algorithm/process.py` | The python file containing your algorithm with the `Process.process()` function |
    | `algorithm/input_output.py` | The python file containing the input and output [dataclasses](https://docs.python.org/3/library/dataclasses.html)  |
    | `pesto/api/config.json`        | A generic configuration file at the disposal of `process.py` for its own configuration |
    | `pesto/api/config_schema.json` | The schema of is a json schema file that specifies what config.json should look like |
    | `pesto/api/description.json`   | Description your processing algorithm |
    | `pesto/api/input_schema.json`  | Specifications of the algorithm's input format |
    | `pesto/api/output_schema.json` | Specifications of the algorithm's output format |
    | `pesto/api/version.json`       | Algorithm version description |

To __package your algorithm with PESTO__, you'll need to :

1. Provide the implementation of your algorithm within the `process()` function in `algorithm/process.py`

2. Specify the API of your algorithm, in other words its input and output formats in `pesto/api/input_schema.json` and `pesto/api/output_schema.json`. 

3. Describe and configure the dependencies in `pesto/api/description.json` and `pesto/build/requirements.json`

!!! tip

    Always start from the [pesto-template](pesto_init.md) as it is already a working PESTO project.

One of the main points of attention is to align schemas of `input_schema.json` and `output_schema.json` with the signature of the `process` function. Defining the input/output schemas can be done in two different ways:

- either the `process()` function takes an `Input` object and returns an `Output` object specified in `input_ouput.py` : in that case, [`pesto schemagen`](pesto_schemagen.md) can generate the schemas for you. This is the easiest and recommended way.

- or the `process()` function takes a set of parameters of your choice and returns an object : in that cas you have to specify by yourself the `input_schema.json` and `output_schema.json` contents. This is recommended for complex input/output structures that require a json schema that can not be inferred by `pesto schemagen`.

## Python algorithm

The `algorithm/process.py` should contains a `Process` class with the `Process.process()` method.

!!! warning
    Depending on the `Process.process()` function signature, you will be able to automatically generate or not the input/output schemas with [`pesto schemagen`](pesto_schemagen.md).

If you can encapsulate the input parameters in the `algorithm.input_output.Input` [dataclass](https://docs.python.org/3/library/dataclasses.html) and the returned objects in the `algorithm.input_output.Output` dataclass, then you can benefit from the [schema generation](pesto_schemagen.md). Simply edit the `algorithm/input_output.py` file to specify the input parameters and the output structure. The signature of the algorithm must be 
```py 
process(input: Input) -> Output
```

If your algorithm `Process.process()` function takes a list of parameters or returns an object that is not an `Output`, then the signature is not compatible with  [`pesto schemagen`](pesto_schemagen.md) : you will have to implement the schemas.

!!! Example "process.py schemagen compatible, or not"
    === "Compatible with schemagen"
        ```python linenums="1" hl_lines="2" title="process.py"
        class Process(object):
            def process(input: Input) -> Output:
                # do some processing on the input and return the result
                return new Output({},{},1.0)
        ```
        ```python linenums="1" title="input_output.py"
        @dataclass
        class Input:
            image:np.array = definition(Definition.Image, required=True, description="Input image")
            dict_parameter:dict = definition(Definition.Metadata, description="A dict parameter")
            
        @dataclass
        class Output:
            partial_result_1: dict = definition(Definition.Metadata)
            partial_result_2: dict = definition(Definition.Metadata)
            integer_output: int = field("Confidence value")
        ```

    === "Manual"
        ```python linenums="1" hl_lines="2" title="process.py"
        class Process(object):
            def process(self, image, dict_parameter) -> dict:
                # do some processing on the input and return the result
                return {
                    'partial_result_1': {},
                    'partial_result_2': {},
                    'confidence': 1.0
                }
        ```
        !!! Warning
            In this case, you also have to define manually the input/output schemas. This is detailed in the next section.

!!! Info
    Images are converted to/from numpy arrays by PESTO. Thus, the `Process.process()` function should expect to receive **numpy arrays** and always return images as **numpy arrays**.

## Input / Output specification

To run, PESTO needs the input and output schema files:

  - `pesto/api/input_schema.json`

  - `pesto/api/output_schema.json`

### With schemagen

If the `Process.process()` function takes an `Input` and returns an `Output`, then you can generate the `input_schema.json` and `output_schema.json`:

```shell
pesto schemagen --force algo-service/
```

!!! Success
    ```text hl_lines="4 8"
      [2022-12-21 13:50:33,830] 82809-INFO schemagen::__class2schema():l59:
      Using the geojson user defined definition from PestoFiles.user_definitions_schema
      [2022-12-21 13:50:33,830] 82809-INFO schemagen::__generate():l32:
      The Input schema is now in algo-service/pesto/api/input_schema.json
      [2022-12-21 13:50:33,831] 82809-INFO schemagen::__class2schema():l59:
      Using the geojson user defined definition from PestoFiles.user_definitions_schema
      [2022-12-21 13:50:33,832] 82809-INFO schemagen::__generate():l32:
      The Output schema is now in algo-service/pesto/api/output_schema.json
    ```

See the documentation of [`pesto schemagen`](pesto_schemagen.md) to see all the supported types.

### Manually

If you do/can not use `pesto schemagen`, then you have to define the processing input and output.
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



