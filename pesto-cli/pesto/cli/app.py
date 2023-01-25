import argparse
import typer
import os
from typing import List
from pathlib import Path

import pkg_resources
from pkg_resources import resource_string

from pesto.common.pesto import PESTO_WORKSPACE
from pesto.cli import build as builder
from pesto.cli.run import app as run_app
from pesto.cli.core.utils import PESTO_LOG
from pesto.version import PESTO_VERSION
from pesto.cli.core.build_config import BuildConfig
from pesto.common.testing.test_runner import TestRunner
from pesto.cli.schemagen import generate

from cookiecutter.main import cookiecutter


ALGO_TEMPLATE_PATH = pkg_resources.get_provider('pesto.cli').__dict__['module_path'] + '/resources/template'

app = typer.Typer()
app.add_typer(run_app, name="run", help="Run pesto processes")

def display_banner() -> None:
    processing_factory_banner = resource_string('pesto.cli.resources', 'banner.txt') \
        .decode('utf-8') \
        .replace(' ---------------', ': {:10s}----'.format(PESTO_VERSION))

    PESTO_LOG.info(processing_factory_banner)

@app.command()
def init(target: str,
         template: str=typer.Option(ALGO_TEMPLATE_PATH,"--template","-t",help="path to the algorithm template"),
         default: bool=typer.Option(False, help="Whether to prompt for values or use default")):
    """
    Initialize a new algorithm in the given target directory
    """
    cmd = "cookiecutter {} --output-dir {}".format(template, target)
    PESTO_LOG.info(cmd)
    PESTO_LOG.info("\nPlease fill necessary information to initialize your template\n")
    res = cookiecutter(template, output_dir=target, no_input=default)
    PESTO_LOG.info("Service generated at {}".format(res))
    
@app.command()
def schemagen(target: str,
    force: bool=typer.Option(False,"--force","-f",help="Force writing the input & output schemas, even if they already exist")):
    """
    Generate the input & output schemas from input_output.py
    """
    generate(target, force)

@app.command()
def build(build_config: str,
          profile: List[str]=typer.Option(list(),"--profile","-p",help="Select specific files to update"),
          cache: str=typer.Option(None,"--cache","-c",help="Select a cache policy: CACHE_UP_TO_PESTO (or C1) or CACHE_UP_TO_PIP_REQ (or C2) or CACHE_UP_TO_ALGO or C3"),
          proxy: str=typer.Option(None,help="Define a proxy to use during docker construction"),
          network: str=typer.Option("host",help="Define a specific network for docker construction")):
    """
    Build docker image with Pesto from given build.json
    """
    builder.build(search_build_config(build_config),profile,proxy,network,cache)
    
@app.command()
def test(build_config: str,
         profile: List[str]=typer.Option(list(),"--profile","-p",help="Select specific files to update"),
         nvidia: bool=typer.Option(False,help="Run docker with nvidia runtime"),
         ssl: bool=typer.Option(False,help="run with SSL"),
         network: str=typer.Option(None,"--network","-n",help="Define a specific network t run docker")):
    """
    Test algorithm from given build.json
    """
    build_config = BuildConfig.from_path(path=search_build_config(build_config), profiles=profile, network=network)
    PESTO_LOG.info('build configuration : {}'.format(build_config))
    pesto_path = Path(build_config.algorithm_path) / 'pesto' / 'tests' / 'resources'
    TestRunner(docker_image_name=build_config.docker_image_name, network=network, nvidia=nvidia, ssl=ssl).run_all(pesto_path)

@app.command()
def list():
    """
    List projects in PESTO workspace
    """
    PESTO_LOG.info('Processing Factory repository path :'.format(PESTO_WORKSPACE))
    PESTO_LOG.info('list of available builds :')

    for name in os.listdir(PESTO_WORKSPACE):
        if name.startswith('.'):
            continue
        for version in os.listdir(os.path.join(PESTO_WORKSPACE, name)):
            id = '{}:{}'.format(name, version)
            PESTO_LOG.info(''' {0} :
            pesto build {0}
             '''.format(id))


def search_build_config(build_config_path: str) -> str:
    PESTO_LOG.debug('search build config ...')

    if ':' in build_config_path:
        PESTO_LOG.info('search {} in PESTO build repository : {}'.format(build_config_path, PESTO_WORKSPACE))
        name, version = build_config_path.split(':')
        build_config_path = os.path.join(PESTO_WORKSPACE, name, version, name)

    if not build_config_path.endswith('.json'):
        PESTO_LOG.warning('build parameter {} is not a json ...'.format(build_config_path))
        build_config_path = os.path.join(build_config_path, 'pesto', 'build', 'build.json')
        PESTO_LOG.warning('search for build.json in {}'.format(build_config_path))
        if not os.path.exists(build_config_path):
            raise ValueError('build.json not found at {}'.format(build_config_path))

    return build_config_path

def main():
    display_banner()
    app()

if __name__ == "__main__":
    main()