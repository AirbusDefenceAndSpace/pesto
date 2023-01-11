# PESTO Cookbook

## How to load resources only once (at server start) : I don't want to reload my model for each prediction ?

Use static variables in Process class.
Ex:
```python
class Process:
    heavy_requirement = None

    def process(self, *args, **kwargs):
        # load only once
        if Process.heavy_requirement is None:
            Process.heavy_requirement = ...

        # use heavy_requirement for processing
        ... 
```

## How to use profiles to factorize PESTO configurations ?

Imagine you want to build two services out of one algorithm implementation :

- cpu : run on CPU with a specific model and requirements,
- gpu : run on GPU with another model and requirements.

In 'pesto/build/' you can use three files to define requirements :

- requirements.json : common requirements,
- requirements.cpu.json : specific CPU requirements,
- requirements.gpu.json : specific GPU requirements.

Then build your service with the '--profile' or '-p' option :

```
pesto build path/to/project -p cpu
pesto build path/to/project -p gpu
```

More details in the [profile](pesto_build.md) section of the PESTO documentation.


## How to use profiles to build variants of a same algorithm ?

For exemple you want to build your algorithm with 2 variants :

- raster : return detections as an image mask,
- vector : return detections as a geometry.

Build your service with the '--profile' or '-p' option :

```
pesto build path/to/project -p raster cpu
pesto build path/to/project -p vector cpu
```

Use 'Pesto.is_profile_active(profile:str)' to check at runtime which profile was used during build.

```python
from pesto.common.pesto import Pesto
class Process:
    def process(self, *args, **kwargs):
        mask_output = ...
        if Pesto.is_profile_active('raster'):
            return mask_output
        if Pesto.is_profile_active('vector'):
            return vectorize(mask_output)
        raise NotImplementedError()
```

## How to install / include files in the docker image ?

Pesto will copy or pip install all your requirements in the output docker image.

You just need to define all your [service requirements](package_configuration.md) in the 'pesto/build/requirements.json' file.

## How to test the service built with PESTO ?

Be sure to have a proper pesto-service python project (use the `pesto init` command).
Then, go in your project `pesto/tests` directory and start editing files.


The `pesto/tests` is composed of :
- some directories (one per processing to be run),
- a `expected_describe.json` file.

Each `pesto/tests/xxx` directory is composed  of :
- an `input` directory matching `pesto/api/input_schema.json`,
- an `output` directory matching `pesto/api/output_schema.json`.

The `input` and `output` directories both describes a json payload (the processing input and output).
Each filename `key.type` in those folders must match an entry in its corresponding `*_schema.json` :
- `key` is the key in the `*_schema.json`,
- `type` is the primitive type of the key :
  - string, float, int,
  - json : dictionaries,
  - *.tif, *.jpg, *.png for images.
  - arrays can be constructed using a folder `key` containing its enumerted items (`1.int`, `2.int`, ...)


ex:
The following describes the correspondance between the file structure and the json payload.

- pesto/tests/input
  - key1.string (containing `text`)
  - key2.int (containing `33`)
  - key3.float (containing `3.14`)
  
```
{
    "key1" : "text",
    "key2" : 33,
    "key3" : 3.14
}
```

More examples are provided in the default pesto template.

Then, it is required to build your project (once).
```
pesto build /path/to/pesto-service -p p1 p2
```

Finally, run the tests :
```
pesto test /path/to/pesto-service -p p1 p2
```

!!! Note

    - No code to write in the template-service
    - Directly fill the directories at the root of `pesto/tests`
    - Run `pesto tests /path/to/pesto-service -p cpu` to test a built docker image with the selected profile.