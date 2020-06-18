# pesto test : test your packaged docker image

PESTO integrate a minimal yet powerful testing framework.

## Basic usage

You must first configure your `pesto/tests/resources` folder by creating a new `my_test_data` folder inside.

The `pesto/tests/resources/my_test_data` must contains :

- input : list of files to create the processing payload,
- output : list of files to create the expected dictionary response from the processing.
 
Then, make sure that `pesto/tests/test_service.py` contains a test pointing to your `my_test_data` folder.

Finally run the following command :
```bash
pesto test /path/to/service-xxx
```

**Alternative:** Use pytest to run the tests :
```bash
pytest /path/to/service-xxx/pesto/tests
```

**Example:**

Each file in the `input` and `output` folder is interpreted following the following rules :

- the extension must be one of 'string', 'int', 'float', 'json' or some image extension (jpg, bmp, tif are supported).

