# Deploying PyTorch in Python via a REST API with PESTO

!!! abstract
	This tutorial is inspired from the official [Deploying PyTorch in Python via a REST API with Flask](https://pytorch.org/tutorials/intermediate/flask_rest_api_tutorial.html) tutorial. 

	In this walkthrough, you will be guided in using PESTO for packaging your Deep Learning Model such that it is ready for deployment in production. You will be able to send processing requests to your newly created web service embedding your own inference model.
	
	This model is a Resnet 50 CNN trained on ImageNet, and takes as input an image and returns one of the 1000 imagenet classes.
	
	During this tutorial you will learn to
	
	- Package a model using PESTO
	- Define the input and output API of you web service
	- Generate the web service Docker image
    - Deploy your webservice
    - Send requests & get responses from the service



## Install PESTO

First, ensure you have PESTO installed in a python 3.6+ environment. Typically, you can use Miniconda as a virtual env.

!!! note
    You should have docker community edition installed and configured in your machine. Refer to [the docker documentation](https://docs.docker.com/engine/install/) for more details.

To install PESTO with pip (see [Get Started](get_started.md)): 

```bash
$ pip install processing-factory
``` 

## Create PESTO project

Next, initialize your PESTO project in the desired repository.

```bash
$ pesto init {PESTO_root_projects_repository_path}
``` 

You are prompted for some information to fill the default template. Here's an example of the display

```text
---------------------------------------------------------------------------------------------------------------------------
  ____  _____ ____ _____ ___        ____                              _                 __            _
 |  _ \| ____/ ___|_   _/ _ \   _  |  _ \ _ __ ___   ___ ___  ___ ___(_)_ __   __ _    / _| __ _  ___| |_ ___  _ __ _   _
 | |_) |  _| \___ \ | || | | | (_) | |_) | '__/ _ \ / __/ _ \/ __/ __| | '_ \ / _` |  | |_ / _` |/ __| __/ _ \| '__| | | |
 |  __/| |___ ___) || || |_| |  _  |  __/| | | (_) | (_|  __/\__ \__ \ | | | | (_| |  |  _| (_| | (__| || (_) | |  | |_| |
 |_|   |_____|____/ |_| \___/  (_) |_|   |_|  \___/ \___\___||___/___/_|_| |_|\__, |  |_|  \__,_|\___|\__\___/|_|   \__, |
                                                                              |___/                                 |___/
-----  ProcESsing facTOry : 1.4.3     -------------------------------------------------------------------------------------

Please fill necessary information to initialize your template

maintainer_fullname [pesto]: Computer Vision
maintainer_email [pesto@airbus.com]: computervision@airbus.com
project_name [algo-service]: pytorch-deployment-tutorial
project_sname [pytorch-deployment-tutorial]:                            
project_short_description [Pesto Template contains all the boilerplate you need to create a processing-factory project]: My first deployment with PESTO
project_version [1.0.0.dev0]: 1.0.0
[2022-12-13 17:44:24,345] 28731-INFO app::init():l44:
Service generated at /tmp/pesto/pytorch-deployment-tutorial
```

It generates the default template in a folder `pytorch-deployment-tutorial` with the following file structure:

```text
pytorch-deployment-tutorial/
├── algorithm
│   ├── __init__.py
│   ├── input_output.py
│   └── process.py
├── __init__.py
├── Makefile
├── MANIFEST.in
├── pesto
│   ├── api
│   ├── build
│   └── tests
├── README.md
├── requirements.txt
└── setup.py
```

You can recognize a python package with a package named `algorithm` and a module `algorithm.process`.
The main processing is defined here (in Python and using your custom libraries if you want to do so)

The folder `pesto` includes the necessary resources to build the docker image containing the service:

- `pesto/api` will specify the input/output of our process in terms of RESTful API
- `pesto/build` will specify resources, docker images, etc ... so that PESTO can build the service with the correct dependencies
- `pesto/test` will contains resources to test & debug your service once built as well as helper scripts to use 


## Your Custom Processing code

!!! tip
    
    Due to the way we will load pesto-defined files in our process.py, (as well as custom dependencies unpacked at specific locations), it is hard to locally test the custom processing code without rewriting part of it to work locally. This is a known difficulty in development, we recommend to wrap your codebase under a custom library or package and to write as little code as possible (loading models, calling the prediction library then formatting the result properly) under process.py

First, we will specify our inference pipeline. Our objective is to use a pretrained Convolutional Neural Network (A Resnet50) from `torchvision` to predict classes for image that will be fed to it.

The model was trained on ImageNet so it should return one amongst 1000 classes when presented with an image.

We will load our model, using the included checkpoints loading function of torchvision, as well as a json file containing the conversion between class indexes and class names (which is stored in `/etc/pesto/config.json`, more on that later).

```python linenums="1" 
import json
import torchvision.models

with open(os.path.join("/etc/pesto/", "config.json"), 'r') as f:
    IMAGENET_CLASS_INDEX = json.load(f)

# Make sure to pass `pretrained` as `True` to use the pretrained weights:
MODEL = models.alexnet(pretrained=True)
# Since we are using our model only for inference, switch to `eval` mode:
MODEL.eval()
```

Resnet model requires the image to be of 3 channel RGB image of size 224 x 224. We will preprocess the image with Imagenet values as well.  

!!! info
	Should you require more information , please refer to the [original tutorial](https://pytorch.org/tutorials/intermediate/flask_rest_api_tutorial.html#inference) as well as the [pytorch documentation](https://pytorch.org)

```python linenums="1" 
    from PIL import Image
    import torchvision.transforms
    # Preprocessing function
    def transform_image(image: Image):
        my_transforms = torchvision.transforms.Compose([
            torchvision.transforms.Resize(255),
            torchvision.transforms.CenterCrop(224),
            torchvision.transforms.ToTensor(),
            torchvision.transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ])
        return my_transforms(image).unsqueeze(0)
```

Now, getting predictions from this model is simple:

```python linenums="1" 
import time 

def predict(image: np.ndarray):
    """
    The core algorithm is implemented here.
    """

    pil_image = Image.fromarray(image)
    tensor = transform_image(image=pil_image)
    outputs = MODEL.forward(tensor)
    _, y_hat = outputs.max(1)
    predicted_idx = str(y_hat.item())
    class_id, class_name = IMAGENET_CLASS_INDEX[predicted_idx]

    result = {'category': class_name, 'time'}

    return result
```

Now we will need to put these functions so that PESTO can properly call them.

Look at `algorithm/process.py`. This is the module that will be loaded by PESTO inside our server and which will be called during preprocessing. 

There is a `Process` class with `on_start()` and `process()` methods.

The `on_start()` method will be called on the first processing request, it is usually useful to load resources etc.

The `process()` function is called during call to `/api/v1/process`, when we want to actually process input data

We want to integrate our previous code into this structure, so your `algorithm/process.py` file should look like this (replace the existing `process.py` file by this code, or write your own)

!!! note
	We did not load the Model in the `Process` class so each method inside the `Process` class is static. 

```python linenums="1" hl_lines="37-39 67 73 93" title="process.py"
import json
import os

import numpy as np
import torch.cuda
import torchvision.models
import torchvision.transforms
from PIL import Image

from algorithm.input_output import Input, Output

# Device Agnostic Code
if torch.cuda.is_available():
    device = torch.device('cuda')
    cpu = torch.device('cpu')
else:
    device = torch.device('cpu')
    cpu = torch.device('cpu')


# Load Classes
with open(os.path.join("/etc/pesto/", "config.json"), "r") as f:
    IMAGENET_CLASS_INDEX = json.load(f)

# Load Model

# Make sure to pass `pretrained` as `True` to use the pretrained weights:
MODEL = torchvision.models.resnet50(pretrained=True)

if torch.cuda.is_available():
    MODEL = MODEL.to(device)

# Since we are using our model only for inference, switch to `eval` mode:
MODEL.eval()


class Process:
    @staticmethod
    def on_start() -> None:
        """
        Process.on_start will be called at server start time.
        If you need to load heavy resources before processing data, this should be done here.
        """
        image = (np.random.random((256, 256, 3)) * 255.0).astype(np.uint8)
        image = Image.fromarray(image)
        tensor = Process.transform_image(image).to(device)
        _ = MODEL.forward(tensor)
        print("DUMMY RUN OK")

    # Preprocessing function
    @staticmethod
    def transform_image(image: Image):
        my_transforms = torchvision.transforms.Compose(
            [
                torchvision.transforms.Resize(255),
                torchvision.transforms.CenterCrop(224),
                torchvision.transforms.ToTensor(),
                torchvision.transforms.Normalize(
                    [0.485, 0.456, 0.406], [0.229, 0.224, 0.225]
                ),
            ]
        )
        return my_transforms(image).unsqueeze(0)

    # Main processing function
    @staticmethod
    def process(input: Input) -> Output:
        """
        The core algorithm is implemented here.
        """

        # PESTO gives images as C,H,W so we will convert them back to H,W,C to convert them as PIL.Image
        image = input.image.transpose((1, 2, 0))
        pil_image = Image.fromarray(image)

        # A tensor with a batch size of 1 (1, C, H, W)
        tensor = Process.transform_image(image=pil_image)

        if torch.cuda.is_available():
            tensor = tensor.to(device)

        # Forward
        outputs = MODEL.forward(tensor)

        if torch.cuda.is_available():
            outputs = outputs.to(cpu)

        # Postprocess
        _, y_hat = outputs.max(1)
        predicted_idx = str(y_hat.item())
        class_id, class_name = IMAGENET_CLASS_INDEX[predicted_idx]

        return Output(category=class_name)
```

```python linenums="1" hl_lines="7 11" title="input_output.py"
from dataclasses import dataclass
from pesto.cli.fields import Definition, field, definition, user_definition
import numpy as np

@dataclass
class Input:
    image:np.array = definition(Definition.Image, required=True, description="Image related to any ImageNet class")
    
@dataclass
class Output:
    category:str = field("Predicted class")
```

!!! danger "About Images Format"
    PESTO decodes input request in a specific way, which means that for images they are provided to the algorithm in Channel,Height,Width format, contrarily to the usual Height,Width,Channel format. This means that a transposition is required to wrap them up in PIL format for example. 
    
	The easiest way to do so is to call `image = image.transpose((1, 2, 0))`

## Generating the input & output schemas

PESTO needs the input and output json schemas for specifying the algorithm API to the end users. It can be done by editing the files. However, since we used the `Input` and `Output` classes for the `process()`'s signature, we can benefit from `pesto schemagen` to generate the schema files:

```shell
pesto schemagen --force {PESTO_root_projects_repository_path}
```

The generated schemas are in `api/input_schema.json` and in `api/output_schema.json` :

!!! Example "Input and output json schemas"
    === "Input"
        ```python linenums="1" title="api/input_schema.json"

        {
            "image": {
              "$ref": "#/definitions/Image",
              "description": "Image related to any ImageNet class"
          },
          "required": [
              "image"
          ]
        }
        ```

    === "Output"
        ```python linenums="1" title="api/output_schema.json"
        {
          "category": {
              "type": "string",
              "description": "Predicted class"
          },
          "required": []
        }
        ```

Visit the schemagen's [checklist](pesto_schemagen.md#schemagen-checklist) to understand how to benefit from the `schemagen` mechanism.

## Configuring the Processing API for our service

Now that we have implemented our processing, we will configure the web service API to map the RestAPI with the processing API.

Let's have a look at the `pesto/api` folder :

```
pesto/api/
├── config.json
├── config_schema.json
├── description.json
├── description.stateful.json
├── input_schema.json
├── output_schema.json
├── user_definitions.json
└── version.json
```

- `config.json` is a static file which will be available 
- `config_schema.json` is a json schema file that specifies what `config.json` should look like
- `description.json` is a json file that contains information about our processing
- `input_schema.json` is the specification of the input payload that is necessary to run `Process.process()`. It will be used to specify what should be sent to the webserver
- `output_schema.json` is the specification of the output response of the processing
- `user_definitions.json` the user definitions (reusable JSON schema objects)
- `description.stateful.json` is an alternative description that will be used with a different profile. The later parts of the tutorial will address this point specifically. 

For more information on jsonschema please refer to [the official documentation](https://json-schema.org/)

### config.json

In `config.json` you can put any information that will be used later to configure your algorithm. This can be useful when used in conjunction with profiles, should you have different configuration for different profiles.

In our use case, we will simply put all the imagenet classes in this file, so that they are readily acessible by the webservice.

Download [this file](https://s3.amazonaws.com/deep-learning-models/image-models/imagenet_class_index.json) and copy it as `config.json` 

Imagenet classes can then be loaded in `process.py` as follows:

```python linenums="1" title="process.py"
# Load Classes
with open(os.path.join("/etc/pesto/", "config.json"), "r") as f:
    IMAGENET_CLASS_INDEX = json.load(f)
```

Now we have to define the json schema (`config_schema.json`) that validates it. Here it is:

```json title="api/config_schema.json" linenums="1" 
{
  "$schema": "http://json-schema.org/draft-06/schema#",
  "title": "tile-object-detection-config",
  "description": "Geo Process API config Schema for Deployment Tutorial",
  "type": "object",
  "patternProperties": {
    "^.*$": {
      "type": "array",
      "items": {
        "type": "string"
      }
    }
  }
}
```

!!! tip
	
	You can use the following code snippet to check for json schema validity in python

```python linenums="1"  hl_lines="10"
import json
import jsonschema

with open('./config.json', 'r') as f:
config = json.load(f)

with open('./config_schema.json', 'r') as f:
schema = json.load(f)

jsonschema.validate(config, schema)
```

### description.json

The `description.json` file contains information that describe your processing. Feel free to fill as much information as possible. Note that those information are INFORMATIVE only and not used anywhere **except for** the `stateful` key which has to set. For now, leave it to `false`, we will come back on it later. 

Here is an example of a `description.json` file that you can copy:

```json title="api/description.json" linenums="1"
{
  "title": "pytorch-deployment-tutorial",
  "name": "pytorch-deployment-tutorial",
  "version": "1.0.0.dev0",
  "description": "My first deployment with PESTO",
  "family": "classification",
  "template": "image-classification",
  "keywords": [
    "classification",
    "resnet",
    "imagenet"
  ],
  "resources": {
    "cpu": 4,
    "gpu": 0,
    "ram": 8
  },
  "asynchronous": false,
  "organization": "Computer Vision",
  "email": "computervision@airbus.com",
  "licence": "Property of Computer Vision, all rights reserved"
}
```

## Defining our packaging & dependencies

Now that we have specified our API, let's take on the building part of PESTO.

The principle of PESTO is that a `Docker` image with a webservice containing your processing will be constructed when we call `pesto build`. The next steps will be configuring PESTO to build a correct docker.

### Python dependencies for the project & requirements.txt

The project we created is a python package and will be installed as such inside our docker. It is possible to specify the python requirements directly in `requirements.txt` as it will be parsed when doing `pip install {our project}`

The alternative method would be to provide a docker base image with everything already installed, but this is a more advanced usage.

For now, the `requirements.txt` file at the root of our project should look like this:

```text
numpy
Pillow
torch>=1.5.0
torchvision>=0.6.0
```

Now let's look at the `pesto/build` folder

```
build/
├── build.json
├── requirements.cpu.json
└── requirements.json
```

### Service Name & build.json

The `build.json` contains automatically generated information that will be used by PESTO later. You should not have to modify it except if you want to change the version

```json title="build/build.json" linenums="1"
{
  "name": "pytorch-deployment-tutorial",
  "version": "1.0.0.dev0",
  "algorithm_path": null,
  "workspace": null
}
```

The docker image you will generate during build will be tagged `name:version`.

### File Dependencies & requirements.json

There are two `requirements.json` files automatically generated. `requirements.gpu.json` defines a profile for GPU support and we will see later how to configure it.

The `requirements.json` file default as such

```json title="requirements.json" linenums="1"
{
  "environments": {},
  "requirements": {},
  "dockerBaseImage": "python:3.6-stretch"
}
```

`dockerBaseImage` is a pointer towards a docker image that will be used to build the webservice. PESTO will inherit from this base image to install itself as well as the process and its dependencies. For now, `python:3.6-stretch` is a good starting point as it contains the necessary resources installed. You can pass a custom docker image to this step, provided your docker client can access it.

`environments` is used to set environment variables. We will set the `$TORCH_HOME` environment variable to ensure we know its location. The `$TORCH_HOME` variable is used by `torchvision` to download weights in specific locations, check [the torch Hub documentation](https://pytorch.org/docs/stable/hub.html) for more details 

```json linenums="1"
  "environments": {
    "TORCH_HOME": "/opt/torch/"
  }
```

`requirements` is helpful to add static resources such as model weights, configs, as well as custom python package. For now, `requirements` support two types of resources:

- static resources inside `.tar.gz` archives that will be uncompressed in environment
- python wheel `.whl` files that can be pip installed

In order to try ourselves this mechanism, we will download the weights for our model. Torchvision models automatically do this by default when the models are called if the weights are not in `$TORCH_HOME`, but in our case we will put the weights ourselves so that no download step is done during runtime

First, download this [file](https://download.pytorch.org/models/resnet50-19c8e357.pth)

```bash
wget https://download.pytorch.org/models/resnet50-19c8e357.pth
```

Then put it into a `.tar.gz` archive accessible via either a uri (`file://`), or an url (`gs://` and `http://` are supported for now). Note that if you would deploy a model into production we recommend uploading resources to a server or committing them alongside your project so that everything is 100% reproducible

```bash
tar -zcvf checkpoint.tar.gz resnet50-19c8e357.pth
```

Now, note the uri of this `checkpoint.tar.gz`. We want to uncompress this file in `/opt/torch/checkpoints/` in our docker. So your requirements file will look like:

```json linenums="1" title="build/requirements.json"
{
  "environments": {
    "TORCH_HOME": "/opt/torch/"
  },
  "requirements": {
    "checkpoints": {
      "from": "file://{PATH_TO_ARCHIVE}/checkpoint.tar.gz",
      "to": "/opt/torch/checkpoints/"
    }
  },
  "dockerBaseImage": "python:3.6-stretch"
}
```

## Building the Service

Now we have everything we need to build our service. The building part is simple:

`pesto build {root of your project}/pytorch-deployment-tutorial`

There will be a lot of logging informing you about what is happening. PESTO is using `/home/$USER/.pesto/{process name}/{process version}` to store resources needed to build the docker containing the service.

Example in our case:

```
pytorch-deployment-tutorial/
└── 1.0.0.dev0
    ├── checkpoints
    │   └── resnet50-19c8e357.pth
    ├── dist
    │   └── pesto_cli-1.0.0rc1-py3-none-any.whl
    ├── Dockerfile
    ├── pesto
    │   └── api_geo_process_v1.0.yaml
    ├── pytorch-deployment-tutorial
    │   ├── algorithm
    │   │   ├── __init__.py
    │   │   └── process.py
    │   ├── __init__.py
    │   ├── Makefile
    │   ├── MANIFEST.in
    │   ├── pesto
    │   │   ├── api
    │   │   │   ├── config.json
    │   │   │   ├── config_schema.json
    │   │   │   ├── description.json
    │   │   │   ├── input_schema.json
    │   │   │   ├── output_schema.json
    │   │   │   ├── service.json
    │   │   │   └── version.json
    │   │   ├── build
    │   │   │   ├── build.json
    │   │   │   └── requirements.json
    │   │   └── tests
    │   │       ├── (...)
    │   ├── README.md
    │   ├── requirements.txt
    │   └── setup.py
    └── requirements
        └── checkpoint.tar.gz
```

If docker build fails you can debug your service directly in this folder.

If the build succeeds you should be able to see your image `docker image ls`:

```
REPOSITORY                   TAG          IMAGE ID       CREATED        SIZE
pytorch-deployment-tutorial  1.0.0.dev0   08342775a658   4 minutes ago  3.48GB
```

## Testing and Usage

Now we want to test if everything goes well, which means:

- Launching the docker container and checking that it responds to http requests
- Checking that the process we just deployed is working correctly

Fortunately, PESTO features a test/usage framework which is the purpose of the `pesto/test` folder

### Booting up the container & first http requests

First, we can verify that we are able to start the container and send very basic requests to it; 

Run `docker run --rm -p 4000:8080 pytorch-deployment-tutorial:1.0.0.dev0` (check the docker documentation should you need help about the various arguments)

This should start the container so that it can be accessed from http://localhost:4000.

In your browser (or using [CURL](https://curl.haxx.se/docs/httpscripting.html)) you can send basic GET requests to your container, such as

- [http://localhost:4000/api/v1/health](http://localhost:4000/api/v1/health) (`CURL -X GET http://localhost:4000/api/v1/health`) with should answer "OK"

- [http://localhost:4000/api/v1/describe](http://localhost:4000/api/v1/describe) (`CURL -X GET http://localhost:4000/api/v1/describe`) which should return a json file

It is recommended that you save said json file, it will be used later on `CURL -X GET http://localhost:4000/api/v1/describe > description.json`

Now the question is: How can I send a properly formated processing request with the payload (my image) that I want to send ?

!!! tip
	If you know all about base64 encoding or sending URI with POST requests, feel free to skip this part.

For the next parts you can safely stop your running container

### Defining Test Resources 

Let's take a look at the `pesto/test` directory

```
tests
├── README.md
├── resources/
│   ├── expected_describe.json
│   ├── test_1/
│   └── test_2/
```

The `resources` folder will be used by the PESTO Test API and be converted to processing requests that will be sent to `/api/v1/process` with the right format. The response will then be compared to the expected response, and act as unit tests. 

!!! note
	In the later part of this tutorial we will showcase three different ways of generating processing payloads and getting responses / comparing to expected responses. Each method can be used in different context, using different abstraction levels.

The first file of interest is the `expected_describe.json`. This file will be compared to the `http://localhost:4000/api/v1/describe` json document returned by the API. This description file can be used to parse the information about the API (input / output schema, description etc...)

You will learn in time how to manually create an `expected_describe.json` from the `pesto/api` folder, for now it is best to copy the `describe.json` file that we generated earlier and to put it as `expected_describe.json`. You can compare this file to the default `expected_describe.json` and notice how the differences translate themselves to the default processing

Now, there are several folders named `test_*`. The purpose of these test folders is that the input payload files are deposited in `input` and the expected response is in `output`

Let's take a look at the test folder:

```text
test_1
├── input
│   ├── dict_parameter.json
│   ├── image.png
│   ├── integer_parameter.int
│   ├── number_parameter.float
│   ├── object_parameter.json
│   └── string_parameter.string
└── output
    ├── areas
    │   ├── 0.json
    │   └── 1.json
    ├── dict_output.json
    ├── geojson.json
    ├── image_list
    │   ├── 0.png
    │   └── 1.png
    ├── image.png
    ├── integer_output.integer
    ├── number_output.float
    └── string_output.string
```

You can see that both input and output have files with extension corresponding to input types. The filenames are matched with the json payload keys.

Now, we are going to write two tests with those two images as input:

![](./img/chelsea.png)

We know that the input key is `image` and the output key is `category` the model should predict  `{"category": "Egyptian_cat"}`

![](./img/favicon.jpg)

We know that the input key is `image` and the output key is `category` the model should predict  `{"category": "mortar"}`

So, your folder structure should now look like:

```
tests/
├── resources
│   ├── expected_describe.json
│   ├── test_1 (cat)
│   │   ├── input
│   │   │   └── image.png <- copy the cat image here
│   │   └── output
│   │       └── category.string <- this should be Egypcatian_cat
│   └── test_2 (pesto)
│       ├── input
│       │   └── image.jpg <- copy the pesto image here
│       └── output
│           └── category.string <- this should be mortar
```

### Using `pesto test` command

The first way of testing your service is to call `pesto test` utility the same way you called `pesto build`.
In order, this command will:

- Run the docker container (the same way we did previously)
- Send requests to `api/v1/describe` and compare with the `expected_describe.json`
- Send process payloads to `api/v1/process` and compare them to the desired outputs

In your project root, run `pesto test .` and check what happens. The logs should show different steps being processed.

You can check the responses and differences between dictionnaries in the .pesto workspace: `/home/$USER/.pesto/tests/pytorch-deployment-tutorial/1.0.0.dev0`

You will find there the results / responses of all the requests, including describes and processings requests. This is a useful folder to debug potential differences.

Should everything goes well, the `results.json` file should look like this

```json title="results.json" linenums="1"
{
  "describe": {
    "NoDifference": true
  },
  "test_1": {
    "NoDifference": true
  },
  "test_2": {
    "NoDifference": true
  }
}
```

!!! note
	`pesto test` is designed not to fail if the requests pass; Instead it will simply compare dictionaries and display / save the differences as well as the responses, so that the user can go look at what happened and check if this is correct. `pesto test` should be used for debug purposed and not for unit test purposes. We will see later how we can use the PESTO test API with pytest to actually run unit tests

### Bonus: Using Pytest & unit testing

Once you're sure and have debugged properly you can write or edit unit tests in `PESTO_PROJECT_ROOT/tests/` (check the autogenerated file `tests/test_service.py` ) and run it with `pytest tests` on your root project

This can be used to ensure non regression on further edits or if you want to do test driver development

### Bonus: Using PESTO Python API to run tests & send requests to model

Should you want to use in a non-scalable way or further test your services, you can have a look at the `{PESTO_PROJECT_ROOT}/scripts/example_api_usage.py` file that exposes the low level python API that is used in `pesto test`

- The `ServiceManager` class is the class used as a proxy for the python Docker API, and is used to pull / run /attach / stop the containers
- The `PayloadGenerator` class is used to translate files to actual json payload for the REST API
- The `EndpointManager` manages the various endpoints of the processes, and act as a front to post/get requests
- The `ServiceTester` is used to validate payloads & responses against their expected values

!!! note 
	This API is a simple example of how to use services packaged with pesto in python scripts. We encourage you to copy/paste and modify the classes should you feel the need for specific use cases, but both this and `pesto test` is not designed for robustness and scalability
	
	We consider the target of `pesto test` capabilities to be the data scientist, integration testing & scalability should be done at production level

## Adding a GPU profile 

In order to create an image with GPU support, we can complete the proposed profile `gpu`.
The file `requirements.gpu.json` can be updated as follows :

```json title="requirements.gpu.json" linenums="1"
{
  "environments": {},
  "requirements": {},
  "dockerBaseImage": "pytorch/pytorch:1.5-cuda10.1-cudnn7-runtime"
}
```

You can now build your GPU enabled microservice :

`pesto build {root of your project}/pytorch-deployment-tutorial -p gpu`


### PESTO Profiles

in order to accomodate for different hardware targets or slight variations of the same process to deploy, PESTO has a built-in capabilities called `profiles`

Basically, PESTO profiles is a  list of **ordered** strings (`gpu stateless`) whose .json files in `build/api` folders sequentially **update** the base file.

To use them, simply add the list of profiles to your PESTO commands: `pesto build {PESTO_PROJECT_ROOT} -p p1 p2` or `pesto test {PESTO_PROJECT_ROOT} -p p1 p2`

The profiles json files are named `{original_file}.{profile}.json`.

For example, for a `description.json`, then the corresponding description.json for the profile gpu would be `description.gpu.json`.

Profile jsons can be partially complete as they only update the base values if the files are present.

Example:

`description.json`: `{"key":"value", "key2":"value2"}`
`description.p1.json`: `{"key":"value3"}`

Then calling `pesto build . -p p1` will generate a `description.json`: `{"key":"value3", "key2":"value2"}` and take all the other files without additionnal profiles.

!!! warning
	Due to the sequential nature of dictionary updates, the profiles are order dependent

If you have a computer with nvidia drivers & a gpu you can try to run `pesto build . -p gpu` and `pesto test . -p gpu --nvidia` which should do the same as above but with gpu support (and actually run the process on gpu)

### Stateful & Stateless services

PESTO supports building [stateless services as well as stateful services](https://nordicapis.com/defining-stateful-vs-stateless-web-services/).

With stateless services, it is expected that the processing replies directly to the processing request with the response. These services should have no internal state and should always return the same result when presented with the same payload

Stateful services can have internal states, and store the processing results to be later queried.

The main difference is that sending a processing request to `api/v1/process` to a stateful service will not return the result but a `jobID`. The job state can be quiered at `GET api/v1/jobs/{jobID}/status` and results can be queried at  `GET api/v1/jobs/{jobID}/results` when the job is done. The response of the latter request will be a json matching the output schema with URI to individual content (that should individually be queried using `GET requests`)

![](img/pesto_stateful.svg)

Try building your previous service with `pesto build . -p stateful` and starting it as previously, 

`docker run --rm -p 4000:8080 pytorch-deployment-tutorial:1.0.0.dev0-stateful`

Then, run the API usage script (`python scripts/example_api_usage`) while having modified the image name to stateful.

This script should send several requests (like pesto test), but the advantage is that it doesn't kill the service afterwards, so it is possible to look at what happened:

- Try doing a get request on `/api/v1/jobs/` you should see a list of jobs
- Grab a job id then do a GET request on `/api/v1/jobs/{jobID}/status`. It should be "DONE"
- Then do a GET request on `/api/v1/jobs/{jobID}/results` to get results

You should get something like

```json linenums="1"
{
  "category": "http://localhost:4000/api/v1/jobs/1080019533/results/category"
}
```

A GET request on the aforementioned URL should return `Egyptian_cat` or `mortar`

## Next Steps

The rest of the documentation should be more accessible now that you have completed this tutorial

!!! tip 
    You should version your PESTO project using **git** so that it is reproducible 

Feel free to send us feedback and ask any question on [github](https://github.com/AirbusDefenceAndSpace/pesto)
