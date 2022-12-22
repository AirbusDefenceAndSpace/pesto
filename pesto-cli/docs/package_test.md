## Testing and Usage

Now we want to test if everything goes well, which means:

- Launching the docker container and checking that it responds to http requests
- Checking that the process we just deployed is working correctly

Fortunately, PESTO features a test/usage framework which is the purpose of the `pesto/test` folder

### Booting up the container & first http requests


If the build succeeds you should be able to see your image with

```bash
docker image ls
```

```
REPOSITORY                                                  TAG          IMAGE ID       CREATED         SIZE
algo-service                                                1.0.0.dev0   f04d96bb57f4   4 minutes ago   1.16GB
```

First, we can verify that we are able to start the container and send very basic requests to it

```bash
docker run --rm -p 4000:8080 algo-service:1.0.0.dev0
```

This should start the container so that it can be accessed from `http://localhost:4000`.

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

```json
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

### Profiles

[//]: # (TODO: Check how it is used)

It is also possible to test if a profile is activated:

```python
from pesto.common.pesto import Pesto
Pesto.is_profile_active('p1')
# True if 'p1' is activated
# False else
```
