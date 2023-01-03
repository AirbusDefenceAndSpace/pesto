# `pesto build` : Package an algorithm

When your project is properly configured (cf. [pesto init](pesto_init.md)), PESTO can build a docker image containing a running web service.


## Basic usage

If your project path is `PESTO_PROJECT_ROOT = /path/to/your/workspace/xxx-service` you can build it using :

```bash
pesto build {PESTO_PROJECT_ROOT}
```

It creates a packaged docker image:

!!! Success "xxx-service:1.0.0.dev0"

By default, the build command use configuration files in the following directories :

```text
xxx-service/pesto/
├── api
└── build
```

!!! Note

    You can find in recipes/docker/pesto-tools a `Dockerfile` to build a PESTO compliant docker image.


## Note on cache

By default, the generated `Dockerfile` uses no cache. 
The main steps of building the docker image are:

0. PIP configuration and update
1. Install PESTO
2. Install PIP requirements listed in requirements.json
3. Copy algorithm files
4. Set ENV variables and copy algorithm configuration and resources from requirements.json

One can force caching a number of the defined steps, by setting a parameter `--cache|-c <VALUE>` to the `pesto build` command:  

```bash
pesto build {PESTO_PROJECT_ROOT} -c <VALUE>
``` 

The `<VALUE>` can be:

* `CACHE_UP_TO_PESTO` or `C1`: cache up to step 1
* `CACHE_UP_TO_PIP_REQ` or `C2`: cache up to step 2
* `CACHE_UP_TO_ALGO` or `C3`: cache up to step 3



## Profiles

In order to accommodate for different hardware targets or slight variations of the same process to deploy, PESTO has a built-in capabilities called `profiles`.

### Set profile

A profile is a 'tag' that can be added between the base name and the extension of any PESTO configuration file.

The profiles json files are named `{original_file}.{profile}.json`.

!!! example

    For a `description.json`, then the corresponding file for the profile `gpu` would be `description.gpu.json`.

The profile specify which configuration files should be used to create the docker image. 
To activate the profile `p1` at the build, run:  

```bash
pesto build {PESTO_PROJECT_ROOT} -p p1
``` 

!!! note
    Profile `.json` can be partially complete as they only update the base values if the files are present.

!!!example

    - `description.json`
    ```json
    {
        "key":"value", 
        "key2":"value2"
    }
    ```

    - `description.p1.json`
    ```json
    {
        "key":"value3"
    }
    ```

    Then calling `pesto build {PESTO_PROJECT_ROOT} -p p1` will generate the `description.json`
    ```json
    {
        "key":"value3", 
        "key2":"value2"
    }
    ```

### Check profile

PESTO provides some helper libraries to detect which profile was used during packaging.

```python
from pesto.common.pesto import Pesto
profile = Pesto.get_profile()
# ex: profile = 'p1' if activated
```

!!! note
    This result can be used to adapt the python process to the different profiles.

### Cascading profiles

PESTO profiles can be combined. Basically, PESTO profiles is a list of **ordered** strings (ex: `gpu`, `stateless`) whose .json files in `build/api` folders sequentially **update** the base file.

To use them, simply add the list of profiles to your PESTO commands: 

```bash
pesto build {PESTO_PROJECT_ROOT} -p p1 p2
``` 


!!! warning
	Due to the sequential nature of dictionary updates, the profiles are order dependent



The `-p p1 p2` option tells PESTO to consider, for each configuration file, the following versions :

- default : xxx.json (always present)
- p1 : xxx.p1.json
- p2 : xxx.p2.json


!!! Warning 
    Profiles do not work recursively yet. Only the root level is compared.


!!! Example
    
    - xxx.json
    ```json
    {
      "base" : "default",
      "field_0" : "default"
    }
    ```
    - xxx.p1.json
    ```json
    {
      "field_0" : "profile P1",
      "field_1" : "profile P1"
    }
    ```
    - xxx.p2.json
    ```json
    {
      "field_0" : "profile P2",
      "field_2" : "profile P2"
    }
    ```

    Will result in the following equivalent `xxx.json` configuration file :
    ```json
    {
      "base" : "default",
      "field_0" : "profile P2",
      "field_1" : "profile P1",
      "field_2" : "profile P2"
    }
    ```

!!! Note
    The following files are supported by the cascading profiles rule

    ```
    pesto/api/
    ├── config.json
    ├── config_schema.json
    ├── description.json
    ├── input_schema.json
    ├── output_schema.json
    └── version.json
    pesto/build/
    ├── requirements.json
    └── build.json
    ```

## build.json
The `pesto/build/build.json` file is special :

- It contains the name and version of the docker image to be built,
- It does not affect the content of the docker image (only it's name). 

[//]: # (TODO: Check this information)

The `build.json` file must be explicitly selected, and is **not supported** by the cascading profile rule :

```bash
pesto build {PESTO_PROJECT_ROOT}/pesto/build/build.p2.json -p p1 p2
```
