import json
import os
import shlex
import shutil
import subprocess
import tarfile
import glob
from pathlib import Path
from typing import List

import wget

from pesto.cli import PROCESSING_FACTORY_PATH
from pesto.cli.core.build_config import BuildConfig
from pesto.cli.core.config_loader import ConfigLoader
from pesto.cli.core.docker_builder import DockerBuilder
from pesto.cli.core.pesto_files import PestoFiles
from pesto.cli.core.utils import PESTO_LOG
from pesto.common.utils import load_json, validate_json, mkdir


def copy_requirement(from_uri: str, target_path: str) -> None:
    mkdir(target_path)
    if from_uri.startswith("gs://"):
        PESTO_LOG.info('copy to : {}'.format(target_path))
        subprocess.call(shlex.split('gsutil cp {0} {1}'.format(from_uri.rstrip(os.path.sep), target_path)))
    elif from_uri.startswith("file://") and os.path.exists(from_uri.replace("file://", "")):
        shutil.copyfile(from_uri.replace("file://", ""), target_path)
    else:
        wget.download(url=from_uri, out=target_path)


class Builder:
    SCHEMA_PATH = os.path.join(PROCESSING_FACTORY_PATH, 'pesto/cli/resources/schema')

    def __init__(self, build_config: BuildConfig):
        PESTO_LOG.info('***** init packaging *****')
        self.build_config = build_config
        self.configs = ConfigLoader.load(build_config)

        PESTO_LOG.info('********** build parameters **********')
        PESTO_LOG.info('{}'.format(json.dumps(build_config.__dict__, indent=4)))
        PESTO_LOG.info('processing factory path : {}'.format(PROCESSING_FACTORY_PATH))

    def conf_validation(self) -> None:
        PESTO_LOG.info('********** validate requirements.json **********')
        requirements_schema = load_json(Builder.SCHEMA_PATH, 'requirements_schema.json')
        validate_json(self.configs[PestoFiles.requirements], requirements_schema)

        PESTO_LOG.info('********** validate config.json **********')
        validate_json(self.configs[PestoFiles.config], self.configs[PestoFiles.config_schema])

    def copy_factory_files(self) -> None:
        PESTO_LOG.info('********** copy factory files **********')
        if os.path.exists(self.workspace):
            shutil.rmtree(self.workspace)
        os.makedirs(self.workspace, exist_ok=True)

        PESTO_LOG.info('workspace created : {}'.format(self.workspace))

        # copy pesto required resources (api_geo_process_v1.0.yaml)
        PESTO_LOG.debug('COPY pesto resources to workspace from: {}'.format(PROCESSING_FACTORY_PATH))
        # shutil.copytree(os.path.join(PROCESSING_FACTORY_PATH, 'pesto/cli'), os.path.join(self.workspace, 'pesto/cli'))
        os.makedirs(os.path.join(self.workspace, "pesto"), exist_ok=True)
        shutil.copyfile(os.path.join(PROCESSING_FACTORY_PATH, 'pesto/cli/resources/doc/api_geo_process_v1.0.yaml'),
                        os.path.join(self.workspace, 'pesto/api_geo_process_v1.0.yaml'))

        # copy algorithm
        target_path = os.path.join(self.workspace, self.build_config.name)
        PESTO_LOG.debug('COPY algorithm to workspace from: {} to: {}'.format(
            self.build_config.algorithm_path,
            target_path))
        shutil.copytree(self.build_config.algorithm_path, target_path)

        # copy/update config files
        shutil.rmtree(os.path.join(target_path, 'pesto', 'api'))
        shutil.rmtree(os.path.join(target_path, 'pesto', 'build'))
        os.makedirs(os.path.join(target_path, 'pesto', 'api'))
        os.makedirs(os.path.join(target_path, 'pesto', 'build'))

        for item in self.configs:
            with open(os.path.join(target_path, 'pesto', item.value), 'w') as _:
                json.dump(self.configs[item], _, indent=4, sort_keys=True)

    def copy_requirements(self) -> None:
        PESTO_LOG.info('********** copy requirements **********')
        requirements = self.configs[PestoFiles.requirements]['requirements']
        for name in requirements.keys():
            from_uri = requirements[name]['from']
            temporary_path = os.path.join(self.workspace, 'requirements', os.path.basename(from_uri))
            target_path = os.path.join(self.workspace, name)

            PESTO_LOG.info('COPY from {} to {}'.format(from_uri, temporary_path))
            copy_requirement(from_uri, temporary_path)

            if from_uri.endswith('tar.gz'):
                PESTO_LOG.info('EXTRACT from {} to {}'.format(temporary_path, target_path))
                with tarfile.open(temporary_path, 'r:gz') as file:
                    file.extractall(path=target_path)

    def copy_pesto_whl(self) -> None:
        PESTO_LOG.info('********** copy local pesto wheel if any **********')
        source_dir = os.path.join(Path.home(), ".pesto/dist")
        dest_dir = os.path.join(self.workspace, 'dist/')
        os.makedirs(dest_dir, exist_ok=True)
        for filename in glob.glob(os.path.join(source_dir, '*.*')):
            PESTO_LOG.info('********** copy {} in {} **********'.format(filename, dest_dir))
            shutil.copy(filename, dest_dir)

    def build_docker_image(self) -> None:
        PESTO_LOG.info('********** build docker image **********')
        DockerBuilder(self.configs[PestoFiles.requirements], self.build_config).build(self.workspace)

    @property
    def workspace(self):
        return self.build_config.workspace


def build(build_config_path: str, profiles: List[str], proxy: str = None, network: str = "host") -> None:
    config = BuildConfig.from_path(path=build_config_path, profiles=profiles, proxy=proxy, network=network)

    builder = Builder(config)
    builder.conf_validation()
    builder.copy_factory_files()
    builder.copy_requirements()
    builder.copy_pesto_whl()
    builder.build_docker_image()
