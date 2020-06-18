import shlex
import subprocess
from typing import List

from pesto.cli.core.utils import PESTO_LOG
from pesto.cli.core.build_config import BuildConfig


def push(build_config_path, registry_path, profiles: List[str]):
    PESTO_LOG.info('Push docker image to registry : {}'.format(registry_path))

    build_config = BuildConfig.from_path(path=build_config_path, profiles=profiles)
    PESTO_LOG.info('build configuration : {}'.format(build_config))

    algo_name = build_config.name
    algo_version = build_config.version
    local_image_name = '{}:{}'.format(algo_name, algo_version)
    remote_image_name = '{}/{}'.format(registry_path, local_image_name)

    print(local_image_name)
    print(remote_image_name)

    PESTO_LOG.info('tag image {} as {}'.format(local_image_name, remote_image_name))
    subprocess.call(shlex.split('docker tag {} {}'.format(local_image_name, remote_image_name)))
    PESTO_LOG.info('push to gcloud : {}'.format(remote_image_name))
    subprocess.call(shlex.split('gcloud docker -- push  {}'.format(remote_image_name)))
