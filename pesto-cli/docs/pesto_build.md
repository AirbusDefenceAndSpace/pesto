# pesto build : package as a docker image

When your project is properly configured (cf. [pesto init](pesto_init.md)), PESTO can build a docker image containing a running web service.


## Basic usage

If your project path is `/path/to/your/workspace/xxx-service` you can build it using :
```bash
pesto build /path/to/your/workspace/xxx-service
```

By default, the build command use configuration files in the following directories : 

- service-xxx/pesto/
    - api
    - build

## Advanced usage : profiles

The PESTO configurations files can be organized by profile.
A profile is a 'tag' that can be added between the base name and the extension of any PESTO configuration file.

### Cascading profiles

PESTO can build a same project based on different profiles with the following commands :
```bash
pesto build /path/to/your/workspace/xxx-service -p p1 p2
```

The `-p p1 p2` option tells PESTO to consider, for each configuration file, the following versions :

- default : xxx.json (always present)
- p1 : xxx.p1.json
- p2 : xxx.p2.json

The build is equivalent to have a default `xxx.json` file build from :

- xxx.json : initialisation as a dict,
- xxx.p1.json : add/update at the dict root level,
- xxx.p2.json : add/update at the dict root level.

**Warning:** Profiles do not work recursively yet. Only the root level is compared.


**Example:** 

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


### build.json
The `pesto/build/build.json` file is special :

- it contains the name and version of the docker image to be built,
- it does not affect the content of the docker image (only it's name). 


The `build.json` file must be explicitly selected, and is **not supported** by the cascading profile rule :
```bash
pesto build /path/to/service-xxx/pesto/build/build.p2.json -p p1 p2
```

### List of supported configuration files :

The following files are supported by the cascading profiles rule :

- api
    - description.json
    - input_schema.json
    - output_schema.json
    - output_content.json
    - config_schema.json
- build
    - build.json
    - config.json
    - requirements.json
    - version.json


## Note on cache
By default, the generated `Dockerfile` uses no cache.  
The main steps of building the docker image are:
0. PIP configuration and update
1. Install PESTO
2. Install PIP requirements listed in requirements.json
3. Copy algorithm files
4. Set ENV variables and copy algorithm configuration and resources from requirements.json

One can force caching a number of the defined steps, by setting a parameter `--cache|-c <VALUE>` to the `pesto build` command.  
The `VALUE` can be:
* *CACHE_UP_TO_PESTO* or *C1*: cache up to step 1
* *CACHE_UP_TO_PIP_REQ* or *C2*: cache up to step 2
* *CACHE_UP_TO_ALGO* or *C3*: cache up to step 3

