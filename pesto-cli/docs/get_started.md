# Get started

Get started with PESTO ! Let's see how to package a simple processing algorithm.

## Prerequisite

  * [python](https://www.python.org/about/gettingstarted/) >= 3.6, <= 3.9
  * [pip](https://pip.pypa.io/en/stable/installation/) or [git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)
  * [docker](https://docs.docker.com/engine/install/)

!!! warning "macOS"

    For macOS users, it is necessary to set the `DOCKER_DEFAULT_PLATFORM`
    ```bash
    export DOCKER_DEFAULT_PLATFORM=linux/amd64
    ```

## Installation

First, install PESTO-CLI in your environment as follows:

=== "Pypi"

    ```bash
    $ pip install processing-factory
    ```

=== "From source"

    ```bash
    $ git clone https://github.com/AirbusDefenceAndSpace/pesto.git
    $ cd pesto && make install
    ```

Now check your installation.

```bash
$ pesto --help
```


```text
---------------------------------------------------------------------------------------------------------------------------
  ____  _____ ____ _____ ___        ____                              _                 __            _
 |  _ \| ____/ ___|_   _/ _ \   _  |  _ \ _ __ ___   ___ ___  ___ ___(_)_ __   __ _    / _| __ _  ___| |_ ___  _ __ _   _
 | |_) |  _| \___ \ | || | | | (_) | |_) | '__/ _ \ / __/ _ \/ __/ __| | '_ \ / _` |  | |_ / _` |/ __| __/ _ \| '__| | | |
 |  __/| |___ ___) || || |_| |  _  |  __/| | | (_) | (_|  __/\__ \__ \ | | | | (_| |  |  _| (_| | (__| || (_) | |  | |_| |
 |_|   |_____|____/ |_| \___/  (_) |_|   |_|  \___/ \___\___||___/___/_|_| |_|\__, |  |_|  \__,_|\___|\__\___/|_|   \__, |
                                                                              |___/                                 |___/
-----  ProcESsing facTOry : 1.4.3     -------------------------------------------------------------------------------------
Usage: pesto [OPTIONS] COMMAND [ARGS]...

Options:
  --install-completion [bash|zsh|fish|powershell|pwsh]
                                  Install completion for the specified shell.
  --show-completion [bash|zsh|fish|powershell|pwsh]
                                  Show completion for the specified shell, to
                                  copy it or customize the installation.
  --help                          Show this message and exit.

Commands:
  build      Build docker image with Pesto from given build.json
  init       Initialize a new algorithm in the given target directory
  list       List projects in PESTO workspace
  run        Run pesto processes
  schemagen  Generate the input & output schemas from input_output.py
  test       Test algorithm from given build.json
```

!!! Success "PESTO is successfully installed"

## Create PESTO project

Create a directory to store your pesto project.

Use the [init](pesto_init.md) command to create a new PESTO project to package your algorithm: 

```bash
export MY_PESTO_DIR=/tmp/pesto
pesto init $MY_PESTO_DIR
```

In prompt, you can edit descriptors of the project (see [init](pesto_init.md)) or press enter to keep the defaults values.

```
---------------------------------------------------------------------------------------------------------------------------
  ____  _____ ____ _____ ___        ____                              _                 __            _
 |  _ \| ____/ ___|_   _/ _ \   _  |  _ \ _ __ ___   ___ ___  ___ ___(_)_ __   __ _    / _| __ _  ___| |_ ___  _ __ _   _
 | |_) |  _| \___ \ | || | | | (_) | |_) | '__/ _ \ / __/ _ \/ __/ __| | '_ \ / _` |  | |_ / _` |/ __| __/ _ \| '__| | | |
 |  __/| |___ ___) || || |_| |  _  |  __/| | | (_) | (_|  __/\__ \__ \ | | | | (_| |  |  _| (_| | (__| || (_) | |  | |_| |
 |_|   |_____|____/ |_| \___/  (_) |_|   |_|  \___/ \___\___||___/___/_|_| |_|\__, |  |_|  \__,_|\___|\__\___/|_|   \__, |
                                                                              |___/                                 |___/
-----  ProcESsing facTOry : 1.4.3     -------------------------------------------------------------------------------------

Please fill necessary information to initialize your template

maintainer_fullname [pesto]: 
maintainer_email [pesto@airbus.com]: 
project_name [algo-service]: 
project_sname [algo-service]: 
project_short_description [Pesto Template contains all the boilerplate you need to create a processing-factory project]: 
project_version [1.0.0.dev0]: 

Service generated at /tmp/pesto/algo-service
```

!!! Note
    The created PESTO Project `algo-service` is created from template and ready to use with a simple processing. 
    See [init](pesto_init.md) for more details on how to tune it for your needs.


## Build project docker image

Create the project docker image containing the default processing web service with [pesto build function](pesto_build.md):

```bash
$ pesto build $MY_PESTO_DIR/algo-service
``` 

All the template requirements and algorithm configuration are used to create the docker image. 
See [configuration](package_configuration.md) to adapt the template to your own algorithm. 

```
---------------------------------------------------------------------------------------------------------------------------
  ____  _____ ____ _____ ___        ____                              _                 __            _
 |  _ \| ____/ ___|_   _/ _ \   _  |  _ \ _ __ ___   ___ ___  ___ ___(_)_ __   __ _    / _| __ _  ___| |_ ___  _ __ _   _
 | |_) |  _| \___ \ | || | | | (_) | |_) | '__/ _ \ / __/ _ \/ __/ __| | '_ \ / _` |  | |_ / _` |/ __| __/ _ \| '__| | | |
 |  __/| |___ ___) || || |_| |  _  |  __/| | | (_) | (_|  __/\__ \__ \ | | | | (_| |  |  _| (_| | (__| || (_) | |  | |_| |
 |_|   |_____|____/ |_| \___/  (_) |_|   |_|  \___/ \___\___||___/___/_|_| |_|\__, |  |_|  \__,_|\___|\__\___/|_|   \__, |
                                                                              |___/                                 |___/
-----  ProcESsing facTOry : 1.4.3     -------------------------------------------------------------------------------------

[...]

=> => naming to docker.io/library/algo-service:1.0.0.dev0  
```

The docker image `algo-service:1.0.0.dev0` is now available.

## Test the docker image

The template algorithm is an image classifier. The `algo-service` PESTO project contains an image to test the algorithm.

![](./img/chelsea.png)

You can use this image to call the built docker image:

```bash
$ pesto run docker '{"image":"file:///opt/algo-service/pesto/tests/resources/test_1/input/image.png"}' algo-service:1.0.0.dev0 /tmp/output_pesto.json
```

It runs the built docker image, get the algorithm prediction on the image and stop the docker container.

```
---------------------------------------------------------------------------------------------------------------------------
  ____  _____ ____ _____ ___        ____                              _                 __            _
 |  _ \| ____/ ___|_   _/ _ \   _  |  _ \ _ __ ___   ___ ___  ___ ___(_)_ __   __ _    / _| __ _  ___| |_ ___  _ __ _   _
 | |_) |  _| \___ \ | || | | | (_) | |_) | '__/ _ \ / __/ _ \/ __/ __| | '_ \ / _` |  | |_ / _` |/ __| __/ _ \| '__| | | |
 |  __/| |___ ___) || || |_| |  _  |  __/| | | (_) | (_|  __/\__ \__ \ | | | | (_| |  |  _| (_| | (__| || (_) | |  | |_| |
 |_|   |_____|____/ |_| \___/  (_) |_|   |_|  \___/ \___\___||___/___/_|_| |_|\__, |  |_|  \__,_|\___|\__\___/|_|   \__, |
                                                                              |___/                                 |___/
-----  ProcESsing facTOry : 1.4.3     -------------------------------------------------------------------------------------
2022-12-14 04:52:36.311 | INFO     | pesto.common.testing.service_manager:run:92 - Starting container with algo-service:1.0.0.dev0 on port 4000
2022-12-14 04:52:41.224 | INFO     | pesto.common.testing.service_manager:run:106 - Container f3cdc9911d3b2278baae0bcd87e8931a4641630d0d5a9d6076cc2b1b2e896e32 started, available at http://localhost:4000
2022-12-14 04:52:41.226 | INFO     | pesto.common.testing.service_manager:run:112 - Trying api/v1/health for 1st time
2022-12-14 04:52:41.398 | INFO     | pesto.common.testing.service_manager:run:114 - Server not yet alive
2022-12-14 04:52:43.399 | INFO     | pesto.common.testing.service_manager:run:117 - Trying api/v1/health for 2th time
2022-12-14 04:52:43.451 | INFO     | pesto.common.testing.service_manager:run:120 - Server alive
2022-12-14 04:52:43.502 | DEBUG    | pesto.common.testing.endpoint_manager:process:44 - {
  "image": "file:///opt/algo-service/pesto/tests/resources/test_1/input/image.png"
}
2022-12-14 04:52:49.380 | DEBUG    | pesto.common.testing.endpoint_manager:process:63 - {
  "image": "iVBORw0KGgoAAAANSUhEUgAAAcMAAAEsCAIAAAAw9k/eAAAgAElEQVR4nGS8WXIkSZIkyiKiqrb4gi32...",

[ ... ]

        "properties": {
          "category": "egyptian_cat",
          "confidence": 0.42
        },
        "type": "Feature"
      }
    ]
  }
}
2022-12-14 04:52:49.392 | INFO     | pesto.common.testing.service_manager:stop:132 - Stopping container f3cdc9911d3b2278baae0bcd87e8931a4641630d0d5a9d6076cc2b1b2e896e32
```

The image is labelled as `egyptian_cat` with a confidence of `0.42`.

!!! Success "The algorithm is successfully packaged as a docker image"
