from pesto.cli.core.build_config import BuildConfig
from pesto.cli.core.docker_builder import DockerBuilder

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
    dockerfile_lines = dockerbuilder.split("\n")
    pythonpath_lines = []
    for line in dockerfile_lines:
       if line[:14] == "ENV PYTHONPATH":
           pythonpath_lines.append(line)

    # then
    expected = 'ENV PYTHONPATH=${PYTHONPATH:-/opt/my-service}'
    assert pythonpath_lines[0] == expected

    expected = 'ENV PYTHONPATH=${PYTHONPATH:+$PYTHONPATH:/opt/my-service}'
    assert pythonpath_lines[1] == expected


