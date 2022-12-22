# `pesto test` : Test the packaged algorithm

PESTO integrate a minimal yet powerful testing framework.

You must first configure your `pesto/tests/resources` folder by creating a new `my_test_data` folder inside.

The `pesto/tests/resources/my_test_data` must contains :

- input : list of files to create the processing payload,
- output : list of files to create the expected dictionary response from the processing.

!!! note
    Available types and format for input and output are detailed in [configuration section](package_configuration.md).

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

!!! note
	`pesto test` is designed not to fail if the requests pass; Instead it will simply compare dictionaries and display / 
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

**Example:**

Each file in the `input` and `output` folder is interpreted following the following rules :

- the extension must be one of 'string', 'int', 'float', 'json' or some image extension (jpg, bmp, tif are supported).



