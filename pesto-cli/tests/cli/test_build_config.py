from pesto.cli.core.build_config import BuildConfig
from pesto.cli.core.docker_builder import DockerBuilder
import os

_sample_pip_config_file="some/dir/pip.conf"
_sample_pip_extra_index_url="https://MYUSER:MYSECRET@some.artifactory.com/private/repo/simple"

def test_docker_image_name():
    # given
    config = BuildConfig(
        name='my-service',
        version='1.2.3',
        profiles=['p1', 'p2']
    )

    # when
    actual = config.docker_image_name

    # then
    expected = '{}:{}-{}'.format(config.name, config.version, '-'.join(config.profiles))
    assert actual == expected


def test_network():
    config = BuildConfig(
        name='my-service',
        version='1.2.3',
        profiles=['p1', 'p2'],
        network='test_network')
    assert config.network == "test_network"


def test_pythonpath():
    # given
    build_config = BuildConfig(
        name='my-service',
        version='1.2.3',
        profiles=['p1', 'p2'],
        workspace=".")
    requirements={"dockerBaseImage":{}, "requirements":{}, "environments":{}}

    dockerbuilder = DockerBuilder(requirements, build_config).dockerfile()

    # when
    actual = dockerbuilder.split("\n")[17]
    dockerfile_lines = dockerbuilder.split("\n")
    for line in dockerfile_lines:
        if line.startswith("ENV PYTHONPATH"):
            actual = line

    # then
    expected = 'ENV PYTHONPATH=$PYTHONPATH${PYTHONPATH:+:}/opt/my-service'
    assert actual == expected

def test_pip_indexes_arg():
    # given
    env_backup = dict(os.environ)
    os.environ["PIP_CONFIG_FILE"] = _sample_pip_config_file
    os.environ["PIP_EXTRA_INDEX_URL"] = _sample_pip_extra_index_url
    if 'DOCKER_BUILDKIT' in os.environ:
        del os.environ['DOCKER_BUILDKIT']
    build_config = BuildConfig(
        name='my-service',
        version='1.2.3',
        profiles=['p1', 'p2'],
        workspace=".")
    requirements={"dockerBaseImage":{}, "requirements":{}, "environments":{}}

    dockerbuilder = DockerBuilder(requirements, build_config).dockerfile()

    if "PIP_CONFIG_FILE" in env_backup:
        os.environ["PIP_CONFIG_FILE"] = env_backup["PIP_CONFIG_FILE"]
    else:
        del os.environ["PIP_CONFIG_FILE"]
    if "PIP_EXTRA_INDEX_URL" in env_backup:
        os.environ["PIP_EXTRA_INDEX_URL"] = env_backup["PIP_EXTRA_INDEX_URL"]
    else:
        del os.environ["PIP_EXTRA_INDEX_URL"]

    # when
    dockerfile_lines = dockerbuilder.split("\n")
    pipconf_line = "LINE_NOT_FOUND"
    for line in dockerfile_lines:
        if line.startswith("COPY pip.conf"):
            pipconf_line = line
            break

    actual_extra_index = "LINE_NOT_FOUND"
    for line in dockerfile_lines:
        if line.startswith("ARG PIP_EXTRA_INDEX_URL="):
            actual_extra_index = line
            break

    # then
    assert pipconf_line == 'COPY pip.conf /etc'
    assert actual_extra_index == 'ARG PIP_EXTRA_INDEX_URL='+_sample_pip_extra_index_url


def test_pip_indexes_secret():
    # given
    env_backup = dict(os.environ)
    os.environ["PIP_CONFIG_FILE"] = _sample_pip_config_file
    os.environ["PIP_EXTRA_INDEX_URL"] = _sample_pip_extra_index_url
    os.environ['DOCKER_BUILDKIT'] = '1'
    build_config = BuildConfig(
        name='my-service',
        version='1.2.3',
        profiles=['p1', 'p2'],
        workspace=".")
    requirements={"dockerBaseImage":{}, "requirements":{}, "environments":{}}

    dockerbuilder = DockerBuilder(requirements, build_config).dockerfile()

    if "PIP_CONFIG_FILE" in env_backup:
        os.environ["PIP_CONFIG_FILE"] = env_backup["PIP_CONFIG_FILE"]
    else:
        del os.environ["PIP_CONFIG_FILE"]
    if "PIP_EXTRA_INDEX_URL" in env_backup:
        os.environ["PIP_EXTRA_INDEX_URL"] = env_backup["PIP_EXTRA_INDEX_URL"]
    else:
        del os.environ["PIP_EXTRA_INDEX_URL"]
    if not "DOCKER_BUILDKIT" in env_backup:
        del os.environ['DOCKER_BUILDKIT']

    # when
    dockerfile_lines = dockerbuilder.split("\n")
    pip_install_lines = []
    for line in dockerfile_lines:
        if " pip install " in line:
            pip_install_lines.append(line)

    # then
    assert len(pip_install_lines) > 0
    for line in pip_install_lines:
        assert " --mount=type=secret,id=pip_config,dst=/etc/pip.conf " in line
        assert " --mount=type=secret,id=extra_index_url " in line
