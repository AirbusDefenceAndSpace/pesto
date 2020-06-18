# pesto project template

## Maintainers

Florent Le Gac : florent@monkeypatch.io
Florient Chouteau : florient.f.chouteau@airbus.com

## Features

This is a cookiecutter compatible project template that can be initiated from the command line.

The template itself features a project with several namespace subpackages to demonstrate how to properly separate code in a project.

## Prerequisites

No requirements.

## How-To generate a project using the project template

Git clone this repository somewhere or `make build` and store the .zip archive generated

In your root directory (the same directory you would be if you wanted to `git clone` a repo) 

`cookiecutter {template_dir/path_to_zip} --output-dir {root_dir}`

You will have to fill several information to generate the project.

This will create a {{project_sname}} folder in root directory. If output-dir unspecified, create a dir in the current work dir.

You can then `cd {{project_sname}}` and `git init` to get everything working

Other options: https://cookiecutter.readthedocs.io/en/latest/advanced/cli_options.html#command-line-options
