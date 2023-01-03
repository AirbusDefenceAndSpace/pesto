# `pesto init` : Create a new packaging project

The first step to package your processing library is to create a new project.

In a terminal :
```bash
$ pesto init /path/to/your/workspace
```

## Project descriptions fields

You will be prompted for some information to fill the default template.

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
project_name [algo-service]: xxx-service
project_sname [algo-service]: xxx-service
project_short_description [Pesto Template contains all the boilerplate you need to create a processing-factory project]: 
project_version [1.0.0.dev0]: 

Service generated at /path/to/your/workspace/xxx-service
```

The following fields can be set to describe your custom algorithm:

- **maintainer_fullname**
- **maintainer_email**
- **project_name**
- **project_sname**: Project short name
- **project_short_description**
- **project_version**

[//]: # (TODO: Add the precise use of each field?)

This will create a new project named `/path/to/your/workspace/xxx-service` with the following structure:

```text
xxx-service/
├── algorithm
│   ├── __init__.py
│   ├── input_output.py
│   └── process.py
├── __init__.py
├── Makefile
├── MANIFEST.in
├── pesto
│   ├── api
│   ├── build
│   └── tests
├── README.md
├── requirements.txt
└── setup.py
```

!!! Note
    The project is ready and setup for a simple processing, but you should [edit the configuration files](package_configuration.md) to tune PESTO to your needs.


## Custom template

If you have many project sharing some information (your company, email, requirements ...) you can create a specific template.

- Copy the default template to a new place for your own template :

```bash
$ pip show processing-factory | grep Location | awk '{print $NF}' > /tmp/pesto_site_packages.txt
$ cp -r `cat /tmp/pesto_site_packages.txt`/pesto_cli/resources/pesto-template /path/to/my_pesto_template
```

- Edit your template to fix the default values.

- Create a new PESTO project using your own template :

```bash
$ pesto init -t /path/to/my_pesto_template /path/to/your/workspace/xxx-service
```

