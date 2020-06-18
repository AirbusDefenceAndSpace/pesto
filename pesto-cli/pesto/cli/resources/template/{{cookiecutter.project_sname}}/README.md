# {{cookiecutter.project_name}}

{{cookiecutter.project_short_description}}

This template allows to create new image processing algorithm.
It is designed to fit the processing-factory.

The template folders reflect the development process :
- api : define the algorithm interface (input, output, config)
- algorithm : implementation of the algorithm
- tests : run automatic tests
- build : package the algorithm

## Contact

For Merge Request please contact :
- {{cookiecutter.maintainer_fullname}}: {{cookiecutter.maintainer_email}}

## Features

*A short paragraph should give a concise (yet complete) description of the project purpose.*

## Description of directories

### algorithm

- process.py : code the algorithm here

Note: Each image in the input schema will be converted by the web service.
This means you don't need to do any conversion from bytes or other file format.
The web service will call the Process.process(image) function passing directly a numpy array.

Note2: The shape of the numpy array will always be passed in the shape (B,H,W) where :
- B is the image band number
- H is the image row number (= height)
- W is the image column number (= width)

### pesto/api

The interface of the algorithm must be defined in the following files :
- config_schema.json : the schema of configuration file for the algorithm
- description.json : Description of the algorithm (title, description, keywords, licence ...) #TODO remove 'version'
- input_schema.json : schema for validation of the algorithm input
- output_schema.json : schema for validation of the algorithm output
- output_content.json : partial content of the json returned by the /describe endpoint: /Outputs/content
- config.json : a default configuration file for packaging the algorithm

### pesto/build

- requirements.json : Defines requirements for running the algorithm.
    - A base docker image must be provided,
    - git repository ('dependencies'),
    - google cloud models ('models'),
    - environment variables ('environment')
- local_requirements.json : optional file used to override requirements.json.
    Each dependency defined in requirements.json is ignored if the same key is defined in local_requirements.json.
- build.json : default build configuration. This is used by the processing-factory to build or deploy the algorithm.

### pesto/tests

Resources for running tests.
See 'pesto/tests/README.md' for more details.

### tests/

Used to define unit tests should you want to write some

### scripts/

Example of docker usage with the low level Pesto API. You can write here any script that could be interesting for you