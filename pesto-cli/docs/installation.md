# Get started

Get started with PESTO ! Let's see how to package a simple processing algorithm.

## Prerequisite

  * python >= 3.6
  * pip
  * docker
  * git

Note: You can find in recipes/docker/pesto-tools a Dockerfile to build a PESTO compliant docker image.

## Installation

First, install PESTO-CLI in your environment. The simplest way to do it for now is as follows:

```bash
git clone https://github.com/AirbusDefenceAndSpace/pesto.git
cd pesto && make install
```

Now check your installation.

```bash
pesto --help
```

## Usage

PESTO-CLI provides the following commands:

- [init](pesto_init.md) : create a new PESTO-PROJ (i.e. PESTO project),
```bash
export MY_PESTO_DIR=/tmp/pesto
pesto init $MY_PESTO_DIR
```
The created PESTO-PROJ is ready to use with a simple processing. See [init](pesto_init.md) for more details on how to tune it for your needs.


- [build](pesto_build.md) : package a PESTO-PWS (create the project docker image containing the default processing web service),
```bash
pesto build $MY_PESTO_DIR/algo-service
``` 
See [build](pesto_build.md) for more details.

- [test](pesto_test.md) : test a PESTO-PWS (deploy the docker image and run some processings),
```bash
pesto test $MY_PESTO_DIR/algo-service
```
See [test](pesto_test.md) for more details.

- list : list all pesto workspaces,
```bash
pesto list
```

You can easily turn on your webservice and check it is running as follows :

* `$MY_PESTO_DIR/algo-service/scripts/start_service.py`
* [http://localhost:4000/api/v1/describe](http://localhost:4000/api/v1/describe)

The list of endpoints can be found [here](endpoints.md)

## PESTO internal workspaces

Pesto uses workspaces for building services and storing partial responses in asynchronous mode.
Finally, automatic testing copy resources (images) to a temporary folder.
Here is a description of the paths where PESTO could write some files :

```
pesto-cli build :                           $HOME/.pesto/service-name/x.y.z/
pesto-cli build requirements (local cache): $HOME/.pesto/.processing-factory-requirements/
pesto-ws async jobs files :                 $HOME/.pesto/.processing/jobs/${job_id}/
pesto-template (unit testing) :             /tmp/pesto/test
```
