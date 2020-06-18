# PESTO : ProcESsing facTOry

PESTO is a packaging tool inspired from pip, maven and similar dependencies managers dedicated to processing algorithms developped in Python.
It contains shell tools to generate all the boiler plate to build an [OpenAPI](https://playground-docs.readthedocs.io) processing web service compliant with the 
[Geoprocessing-API](https://airbusgeo.github.io/geoapi-viewer/?url=https://raw.githubusercontent.com/AirbusDefenceAndSpace/geoprocessing-api/master/1.0/api_geo_process.yaml). 

PESTO is designed to ease the process of packaging a Python algorithm as a processing web service into a docker image. The deployment in production of a web service becomes now as easy as filling few configuration files.

PESTO is composed of the following components:

- PESTO-CLI : the command line interface used to create a pesto project and package processing algorithms.
- PESTO-PROJ : the project workspace created by PESTO to configure the packaging process of your algorithm.
- PESTO-PWS : the processing web services, as docker images, created by pesto to expose your algorithm.

![](img/pesto.svg)

## Who needs PESTO ?

PESTO was designed by data scientists and processing integrators to optimize and standardize the delivery process from the development of a analytics solution to its integration in a scalable cloud solution. Therefore, PESTO targets as well data scientists wanting their solution to be integrated in large scale solutions, as system integrators wanting to integrate and maintain up-to-date analytics solutions.

PESTO mainly targets the impementation of a web service compliant with the [Geoprocessing-API](https://airbusgeo.github.io/geoapi-viewer/?url=https://raw.githubusercontent.com/AirbusDefenceAndSpace/geoprocessing-api/master/1.0/api_geo_process.yaml). However, it perfectly fits any image processing solution and can even be applied to any processing.

For image processing solutions, PESTO offers mecanisms to indifferently feed algorithms with images as hyperlinks or base64 encoded data as far as the Image type is used, see pesto/ressources/schema/definitions.json. For that purpose, [raster.io](https://rasterio.readthedocs.io/en/latest/) is used.

PESTO ships with default json schemas to define your web service API, look at pesto/ressources/schema/definitions.json. But of course, you can fully tune your API by adding your own schemas. A complementary github project was created to favor the reuse of data types definition as well as services definition, [pesto-schema](https://github.com/AirbusDefenceAndSpace/pesto-schema).


## Main features
Currently, PESTO offers following key features:

* Code generator for a standardized processing web-service,
* Synchronous / asynchronous processing,
* Embedded description of required ressources for deployment in the cloud,
* Testing framework for the PESTO web service,
* Support nvidia docker for GPU accelerated computing,
* Simple interface to include you own runtime dependencies,
* Possibility to choose you root docker image for fine grained tuning of dependencies,
* Version management of web-services.



## Contacts
Coming soon ...
