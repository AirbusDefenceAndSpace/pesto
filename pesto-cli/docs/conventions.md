# Conventions: using PESTO properly


## Image format (numpy array)
PESTO is based on numpy arrays to send to or receive from the packaged algorithm.
The convention is to encode images as arrays with 3 dimensions (C,H,W) :

- C is the channel number
- H is the lines number
- W is the columns number

For example, an RGBA image of dimension 256x256 should be encoded as a numpy array of shape (4,256,256).


## Defining requirements

PESTO can handle requirements in many format (using the 'pesto/build/requirements.json' file) :

- wheel : with 'python setup.py bdist_wheel' on your project and with type 'pip' in 'requirements.json'
- tar.gz : 'python setup.py sdist' on your project and with type 'pip' in 'requirements.json'
- tar.gz : with no type defined, the archive will just be unpacked in the docker image
- tar.gz : (DEPRECATED) with type 'python', the archive will be unpacked and its path added to the PYTHON_PATH.

**Warning** : The tar.gz with type 'python' usage is DEPRECATED and will fail with an archive build with setuptools.
Such an archive contains a root folder that should be removed when adding the path to PYTHON_PATH.


## Automatic Integration Test

PESTO helps you automate testing :

- create a 'test' folder in '{pesto_project_path}/pesto/tests/features/reosurces/' directory,
- add one file per entry in your expected input (cf. 'pesto/api/input_schema.json'),
- deploy your PESTO project : pesto deploy {pesto_project_path}
- if the test fails : read the instructions to make the test pass !

## Cascading profiles : reusable configuration

PESTO supports multiple configurations files organized in [profiles](pesto_build.md).


## Delivery name convention

Given a `build.json` file :
```json
{
  "name": "service-xxx",
  "version": "a.b.c"
}
```

and the build command :
```bash
pesto build build.json -p p1 p2
```

The packaged docker image is automatically named :
```
service-xxx:a.b.c-p1-p2
```

## Docker image naming

Docker images naming convention is : 

* `{ service-name }:{version}` when no profile is used
* `{ service-name }:{version}-stateful` when no profile is used and the service is asynchronous.
* `{ service-name }:{version}-{profile}` when a profile is specified
* `{ service-name }:{version}-{profile}-stateful` when a profile is specified and the service is asynchronous.

