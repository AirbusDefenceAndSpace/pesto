# `pesto test` : Test the packaged algorithm

PESTO integrate a minimal yet powerful testing framework.

You must first configure your `pesto/tests/resources` folder by creating a new `my_test_data` folder inside:

```
tests
├── README.md
└── resources/
    ├── expected_describe.json
    └── my_test_data/
```

The `pesto/tests/resources/my_test_data` must contains :

- **input** : list of files to create the processing payload
- **output** : list of files to create the expected dictionary response from the processing

The `input` and `output` directories both describes a json payload (the processing input and output).
Each filename `key.type` in those folders must match an entry in its corresponding `*_schema.json` :

!!! Note "key.type files"

    `key` is the variable name of the input/output

    `type` is the primitive type of the key :

    - `*.string`, `*.float`, `*.int`
    - `*.json` : dictionaries
    - `*.tif`, `*.jpg`, `*.png` for images.
    - arrays can be constructed using a folder `key` containing its enumerated items (`1.int`, `2.int`, ...)


!!! Example

    ```text
    my_test_data
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


!!! Note "json payload"

    ```
    pesto/tests/resources/my_test_data/input
    ├── key1.string (containing 'text')
    ├── key2.int (containing '33')
    └── key3.float (containing '3.14')
    ```

    Results in the following 'input' payload:

    ```
    {
        "key1" : "text",
        "key2" : 33,
        "key3" : 3.14
    }
    ```


Then, make sure that `pesto/tests/test_service.py` contains a test pointing to your `my_test_data` folder.

Finally, run the following command :

=== "pesto"

    ```bash
    $ pesto test /path/to/service-xxx
    ```

=== "pytest  (alternative)"

    ```bash
    $ pytest /path/to/service-xxx/pesto/tests
    ```

```asciidoc
Usage: pesto test [OPTIONS] BUILD_CONFIG

  Test algorithm from given build.json

Arguments:
  BUILD_CONFIG  [required]

Options:
  -p, --profile TEXT      Select specific files to update
  --nvidia / --no-nvidia  Run docker with nvidia runtime  [default: no-nvidia]
  --ssl / --no-ssl        run with SSL  [default: no-ssl]
  -n, --network TEXT      Define a specific network t run docker
  --help                  Show this message and exit.
```
!!! note
    `pesto test` is designed not to fail if the requests pass. Instead, it will simply compare dictionaries and display / 
     save the differences as well as the responses, so that the user can go look at what happened and check if this is correct.
     
    `pesto test` should be used for debug purposed and not for unit test purposes.

In basic template, two test are implemented (`test_1` & `test_2`) with two images and their output. They successfully pass as:

```text
---------------------------------------------------------------------------------------------------------------------------
  ____  _____ ____ _____ ___        ____                              _                 __            _
 |  _ \| ____/ ___|_   _/ _ \   _  |  _ \ _ __ ___   ___ ___  ___ ___(_)_ __   __ _    / _| __ _  ___| |_ ___  _ __ _   _
 | |_) |  _| \___ \ | || | | | (_) | |_) | '__/ _ \ / __/ _ \/ __/ __| | '_ \ / _` |  | |_ / _` |/ __| __/ _ \| '__| | | |
 |  __/| |___ ___) || || |_| |  _  |  __/| | | (_) | (_|  __/\__ \__ \ | | | | (_| |  |  _| (_| | (__| || (_) | |  | |_| |
 |_|   |_____|____/ |_| \___/  (_) |_|   |_|  \___/ \___\___||___/___/_|_| |_|\__, |  |_|  \__,_|\___|\__\___/|_|   \__, |
                                                                              |___/                                 |___/
-----  ProcESsing facTOry : 1.4.3     -------------------------------------------------------------------------------------

[ ... ]

INFO     | pesto.common.testing.test_runner:run_all:108 - --- Tests Results ---
INFO     | pesto.common.testing.test_runner:run_all:109 - {
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
INFO     | pesto.common.testing.test_runner:run_all:110 - --- Copying tests outputs to /tmp/pesto/tests/algo-service/1.0.0.dev0
```
