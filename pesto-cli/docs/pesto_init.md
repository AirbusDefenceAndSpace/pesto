# pesto init : create a new project

The first step to package your processing library is to create a new project.
We encourage the following naming convention :

- given xxx a short name for your processing :
- then call xxx-lib : the processing library,
- and call xxx-service : the PESTO packaging project.

## Basic usage

In a terminal :
```bash
pesto init /path/to/your/workspace
```

This will create a new project named "/path/to/your/workspace/xxx-service". The project is ready and setup for a simple processing, but you should at least edit some configuration files to tune PESTO to your needs.

1. define the API
    - pesto/api/input_schema.json : json schema describing the input payloads,
    - pesto/api/output_schema.json : json schema describing the output payloads, 

1. implement your process
    - algorithm/process.py : implementation of the processing,

1. package
    - pesto/api/description.json : informative description of the algorithm including deployment requirements,
    - pesto/build/requirements.json : required files and library (your model is defined here) to build the web service.

# Advanced usage

If you have many project sharing some information (your company, email, requirements ...) you can create a specific template.

- Copy the default template to a new place for your own template :

```bash
pip show processing-factory | grep Location | awk '{print $NF}' > /tmp/pesto_site_packages.txt
cp -r `cat /tmp/pesto_site_packages.txt`/pesto_cli/resources/pesto-template /path/to/my_pesto_template
```

- Edit your template to fix the default values.

- Create a new PESTO project using your own template :

```bash
pesto init -t /path/to/my_pesto_template /path/to/your/workspace/xxx-service
```

