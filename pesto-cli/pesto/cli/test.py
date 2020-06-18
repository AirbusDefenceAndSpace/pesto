from pathlib import Path

from pesto.cli.core.build_config import BuildConfig
from pesto.cli.core.utils import PESTO_LOG
from pesto.common.testing.test_runner import TestRunner


def test(build_config_path, profiles, nvidia=False):
    build_config = BuildConfig.from_path(path=build_config_path, profiles=profiles)
    PESTO_LOG.info('build configuration : {}'.format(build_config))

    pesto_path = Path(build_config.algorithm_path) / 'pesto' / 'tests' / 'resources'

    TestRunner(docker_image_name=build_config.docker_image_name, nvidia=nvidia).run_all(pesto_path)
