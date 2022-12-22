# Create PESTO project

The first step to package your processing library is to create a new project.
We encourage the following naming convention :

- given xxx a short name for your processing :
- then call xxx-lib : the processing library,
- and call xxx-service : the PESTO packaging project.


In a terminal, use the [pesto init command](pesto_init.md) to create a PESTO project in the desired repository. :

```shell
pesto init /path/to/your/workspace
```

You will be prompted for some information to fill the default template:

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

Service generated at /path/to/your/workspace/algo-service
```

You can press ENTER to let the default values of the project description fields.

This will create a new project named "/path/to/your/workspace/xxx-service" with the following structure:

```text
pytorch-deployment-tutorial/
├── ...
├── Makefile
├── algorithm
│   ├── ...
│   ├── input_output.py
│   └── process.py
├── pesto
│   ├── api
│   │   ├── ...
│   │   ├── description.json
│   │   ├── description.stateful.json
│   │   ├── input_schema.json
│   │   ├── output_schema.json
│   │   └── user_definitions.json
│   ├── build
│   │   ├── build.json
│   │   ├── requirements.gpu.json
│   │   └── requirements.json
│   └── tests
├── requirements.txt
└── ...
```

!!! Note
    The project is ready and setup for a simple processing, but you should at least [edit some configuration files](package_configuration.md) to tune PESTO to your needs.

