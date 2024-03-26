# PESTO : ProcESsing facTOry

## What is PESTO ?

PESTO is a packaging tool inspired from pip, maven and similar dependencies managers.
It contains shell tools to generate all the boiler plate to build an [OpenAPI](https://playground-docs.readthedocs.io) processing web service compliant with the 
[Geoprocessing-API](https://airbusgeo.github.io/geoapi-viewer/?url=https://raw.githubusercontent.com/AirbusDefenceAndSpace/geoprocessing-api/master/1.0/api_geo_process.yaml). 

PESTO is designed to ease the process of packaging a Python algorithm as a processing web service into a docker image. The deployment of a web service becomes now as easy as filling few configuration files.

PESTO is composed of the following components:

- `pesto-cli` : the command line interface used to create a PESTO project and package processing algorithms.
- `pesto-ws`: the processing web services, as docker images, created by PESTO to expose your algorithm.
- `pesto-project` : the project workspace created by `pesto init` to configure the packaging process of your algorithm.


![](img/pesto.svg)

## Who needs PESTO ?

PESTO was designed by data scientists and processing integrators to optimize and standardize the delivery process from the development of a analytics solution to its integration in a scalable cloud solution. Therefore, PESTO targets as well data scientists wanting their solution to be integrated in large scale solutions, as system integrators wanting to integrate and maintain up-to-date analytics solutions.

PESTO mainly targets the implementation of a web service compliant with the [Geoprocessing-API](https://airbusgeo.github.io/geoapi-viewer/?url=https://raw.githubusercontent.com/AirbusDefenceAndSpace/geoprocessing-api/master/1.0/api_geo_process.yaml). However, it perfectly fits any image processing solution and can even be applied to any processing.


## Main features

PESTO ships with default json schemas to define your web service API, look at `pesto/ressources/schema/definitions.json`. 
But of course, you can fully tune your API by adding your own schemas. 
A complementary github project was created to favor the reuse of data types definition as well as services definition, [pesto-schema](https://github.com/AirbusDefenceAndSpace/pesto-schema).


Currently, PESTO offers following key features:

* Code generator for a standardized processing web-service,
* Synchronous / asynchronous processing,
* Embedded description of required resources for deployment in the cloud,
* Testing framework for the PESTO web service,
* Support nvidia docker for GPU accelerated computing,
* Simple interface to include you own runtime dependencies,
* Possibility to choose you root docker image for fine grained tuning of dependencies,
* Version management of web-services.


## Who uses PESTO

PESTO is currently used by Airbus Defense and Space / Connected Intelligence.

PESTO is under integration by the Airbus Defense and Space / Space Systems Oasis project. It is used to integrate and manage algorithms for TM/TC analysis.

PESTO is under integration by Airbus Defense and Space / Space Systems in its ground segment image chain.

Workshops have been taking place with end-users in order define a solution that first could be integrated in our ground segment product lines. They have contributed to the definition of the product and have validated its integration in their own software stack.

## PESTO roadmap

PESTO was thought to accelerate the integration in our products of Deep Learning algorithms, being developed by Airbus or by partners. That is why, one of the first priorities is to make it open source.

PESTO was initially designed for image processing in mind. Some specificities were then included in the runtime. Our second priority is to set up mechanisms to include user data converters as plugins and to support various Linux families.

PESTO needs to be orchestrated. Simple tutorials and examples to deploy PESTO at scale and manage distributed processing have to be written in order to foster its acceptance by the community.

PESTO testing and deployment framework still need additional effort to offer a complete workflow towards continuous deployment and validation.


## Contacts

- Feel free to send us feedback and ask any question on [github](https://github.com/AirbusDefenceAndSpace/pesto)

- There are some advanced usage & tips in the [pesto cookbook](details_cookbook.md). 
If you find a use case that is not documented, feel free to submit a PR on [github](https://github.com/AirbusDefenceAndSpace/pesto) to update the documentation
