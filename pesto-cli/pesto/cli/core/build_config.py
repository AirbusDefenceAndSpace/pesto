import json
import os
from pathlib import Path
from typing import List
from urllib.parse import urlparse

from pesto.common.pesto import PESTO_WORKSPACE
from pesto.common.utils import load_json


class BuildConfig:

    @staticmethod
    def from_path(path: str,
                  profiles: List[str] = None,
                  proxy: str = None,
                  pip_config_file: str = None,
                  pip_extra_index: str = None,
                  use_buildkit: bool = False,
                  network: str = None
                  ):
        assert path is not None



        build_config = load_json(path)
        return BuildConfig(
            name=build_config['name'],
            version=build_config['version'],
            profiles=profiles,
            workspace=build_config.get('workspace'),
            algorithm_path=build_config.get('algorithm_path') or str(Path(path).parent.parent.parent),
            proxy=proxy,
            pip_config_file=pip_config_file,
            pip_extra_index=pip_extra_index,
            use_buildkit=use_buildkit,
            network=network)

    def __init__(self,
                 name: str = None,
                 version: str = None,
                 profiles: List[str] = None,
                 workspace: str = None,
                 algorithm_path: str = None,
                 proxy: str = None,
                 pip_config_file: str = None,
                 pip_extra_index: str = None,
                 use_buildkit: bool = False,
                 network: str = None):
        self.name = name
        self.version = version
        self.algorithm_path = algorithm_path

        self.profiles = profiles or []
        self.proxy = proxy or ''
        self.network = network
        self.pip_config_file = pip_config_file or os.environ.get('PIP_CONFIG_FILE')
        self.pip_extra_index = pip_extra_index or os.environ.get('PIP_EXTRA_INDEX_URL')
        self.use_buildkit = use_buildkit or (os.environ.get('DOCKER_BUILDKIT') == '1')
        self.workspace = workspace or os.path.join(PESTO_WORKSPACE, self.name, self.full_version)

    @property
    def full_version(self):
        if self.profiles is not None and len(self.profiles) > 0:
            profile_string = '-'.join(self.profiles)
            return '{}-{}'.format(self.version, profile_string)
        return self.version

    @property
    def docker_image_name(self):
        return '{}:{}'.format(self.name, self.full_version)

    def to_dict(self) -> dict:
        return {
            'name': self.name,
            'version': self.full_version,
            'workspace': self.workspace,
            'algorithm_path': self.algorithm_path
        }

    def __repr__(self) -> str:
        return json.dumps(self.to_dict(), indent=2)
