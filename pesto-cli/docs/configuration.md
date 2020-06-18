# Configuration of your PESTO web service


PESTO configuration is done in two steps :

- edit each json configuration file in `pesto/api` directory,
- call your algorithm library from the `algorithm/process.py` entry point.

**Note:** Always start from the [pesto-template](pesto_init.md) as it is already a working PESTO project.

## Basic usage

### Input / Output json validation

The first thing to do is define the processing input and output.
The REST API use json to communicate with external services or users.
We then use [JSON schema](https://json-schema.org/) to validate input payloads. 

- pesto/api/input_schema.json : specify the input validation schema,
- pesto/api/output_schema.json : specify the output validation schema.

### Requirements

PESTO provides a generic way to include any files in the final docker image using the `pesto/build/requirements.json` file :
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
  }
}
```

The following fields are required :

- dockerBaseImage : the docker image to use as a base,
- environments: some user defined variables,
- requirements: A (from,to) list, where 'from' is an URI to some files and 'to' is the target path in the docker image.

Based on the "type" attribute, pesto will :
- python : add the "to" path to the PYTHONPATH,
- pip : pip install the wheel archive,
- default : simply copy the files (uncompressed the archive).

**Compressed files:**
Pesto suport 'tar.gz' archives.
The files are always uncompressed (if needed) before being copied.

**Advanced:**
Each requirement accepts an optional 'type' field :

- python : will add the 'to' path to the PYTHON_PATH environment variable,
- pip : will run a 'pip install' command on the provided wheel or setuptools compatible 'tar.gz' archive.


### Python entry point

The `algorithm/process.py` should contains a 'Process' class with the 'Process.process()' method.
Be sure to match the `input_schema.json` and `output_schema.json` in the 'Process.process()' method arguments and result.

**Important:** Images are converted to/from numpy arrays by PESTO. Thus, the 'Process.process()' method should expect to receive numpy arrays and always return images as numpy arrays.

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
## Advanced usage

### Profile specific implementation

PESTO provides some helper libraries (pesto-common) to detect which profile was used during packaging.
If multiple version of an algorithm must be maintained, it is advised to :

- create multiple python implementation of the 'Process' class (one per file),
- use the `pesto_common.pesto_util.is_profile_active()` to check the current profile,
- select the proper implementation of 'Process' to import.

The following is an example using pesto profiles to switch from one algo to another at build time.

```python
from pesto.common.pesto import Pesto

if Pesto.is_profile_active('v1'):
    from algorithm import process_v1
    Process = process_v1.Process
elif Pesto.is_profile_active('v2'):
    from algorithm import process_v2
    Process = process_v2.Process
else:
    from algorithm import process_v3
    Process = process_v3.Process
```
