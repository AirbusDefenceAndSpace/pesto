import os
import shlex
import subprocess
from typing import List

from jinja2 import Environment, FileSystemLoader

from pesto.cli import PROCESSING_FACTORY_PATH
from pesto.cli.core.build_config import BuildConfig
from pesto.cli.core.utils import PESTO_LOG


class DockerBuilder(object):

    @staticmethod
    def load_template():
        env = Environment(
            loader=FileSystemLoader(os.path.join(PROCESSING_FACTORY_PATH, 'pesto/cli/resources')),
            trim_blocks=True,
            variable_start_string='${',
            variable_end_string='}'
        )
        template = env.get_template('Dockerfile')
        return template

    def __init__(self, requirements: dict, build_config: BuildConfig):
        self.build_config = build_config
        self.algo_name = build_config.name
        self.base_image = requirements['dockerBaseImage']
        self.requirements = requirements['requirements']
        self.environments = requirements['environments']

    def build(self, path: str) -> None:
        dockerfile = self.dockerfile()

        path = os.path.join(path, 'Dockerfile')
        with open(path, 'w+') as file:
            file.write(dockerfile)

        docker_image_name = self.build_config.docker_image_name
        cmd = "docker build --no-cache"
        if self.build_config.network is not None:
            cmd = "{} --network='{}'".format(cmd, self.build_config.network)
        cmd = "{} -t {} {}".format(cmd, docker_image_name, self.build_config.workspace)
        subprocess.call(shlex.split(cmd))

    def dockerfile(self):
        template = self.load_template()
        return template.render(
            base_image=self.base_image,
            algo_name=self.algo_name,
            pip_extra_index=self.build_config.pip_extra_index,
            pip_proxies=self.build_config.pip_proxies,
            env_variables=self._env_variables(),
            pip_requirements=self._pip_requirements(),
            resources_requirements=self._resources()
        )

    def _env_variables(self):
        return {
            'PESTO_PROFILE': self.build_config.full_version,
            **self.environments,
            'PYTHONPATH': "".join(["$PYTHONPATH${PYTHONPATH:+:}", self._python_path])
        }

    @property
    def _python_path(self) -> str:
        return ':'.join([
            '/opt/{}'.format(self.algo_name),
            *[self.requirements[_]['to'] for _ in self._filter_requirements(['python'])]
        ])

    def _filter_requirements(self, types: List[str], include: bool = True):
        def select(req: dict):
            if include:
                return self.requirements[req].get('type', None) in types
            return self.requirements[req].get('type', None) not in types

        return filter(select, self.requirements)

    def _pip_requirements(self):
        pip_requirements = self._filter_requirements(['pip'])
        output = [os.path.basename(self.requirements[_]['from']) for _ in pip_requirements]
        PESTO_LOG.info('pip requirements : {}'.format(output))
        return output

    def _resources(self):
        resources_requirements = self._filter_requirements(['pip'], include=False)
        output = {(name, self.requirements[name]['to']) for name in resources_requirements}
        PESTO_LOG.info('resources requirements : {}'.format(output))
        return output
