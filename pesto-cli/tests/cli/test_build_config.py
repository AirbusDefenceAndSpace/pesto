from pesto.cli.core.build_config import BuildConfig


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
    
