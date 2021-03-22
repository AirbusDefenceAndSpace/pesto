import argparse
import os
from typing import Any

import pkg_resources
from pkg_resources import resource_string

from pesto.common.pesto import PESTO_WORKSPACE
from pesto.cli import build, init, list as list_builds, test
from pesto.cli.core.utils import PESTO_LOG
from pesto.version import PESTO_VERSION

ALGO_TEMPLATE_PATH = pkg_resources.get_provider('pesto.cli').__dict__['module_path'] + '/resources/template'


def display_banner() -> None:
    processing_factory_banner = resource_string('pesto.cli.resources', 'banner.txt') \
        .decode('utf-8') \
        .replace(' ---------------', ': {:10s}----'.format(PESTO_VERSION))

    PESTO_LOG.info(processing_factory_banner)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()

    subparsers = parser.add_subparsers(dest='subcommand', title='subcommands', help='Valid subcommands')
    subparsers.required = True

    # init
    parser_init = subparsers.add_parser('init')
    parser_init.add_argument('-t', '--template', help='path to the algorithm template', default=ALGO_TEMPLATE_PATH)
    parser_init.add_argument('target', help='path to the new algorithm folder')

    # build
    parser_build = subparsers.add_parser('build')
    parser_build.add_argument('build_config', help='path to build.json')
    parser_build.add_argument('-p', '--profile', nargs='+', help='Select specific files to update',
                              default=None)
    parser_build.add_argument('--proxy', help='Define a proxy url to use during docker construction',
                              default=None)
    parser_build.add_argument('-n', '--network', help='Define a specific network for docker construction',
                              default="host")

    # test
    parser_test = subparsers.add_parser('test')
    parser_test.add_argument('build_config', help='path to build.json')
    parser_test.add_argument('-p', '--profile', nargs='+', help='Select specific files to update',
                             default=None)
    parser_test.add_argument('--nvidia',  action='store_true', default=False, help='Run docker with nvidia-runtime')
    parser_test.add_argument('-n', '--network', help='Define a specific network to run docker',
                              default=None)

    # # list builds
    # parser_list = subparsers.add_parser('list')

    return parser.parse_args()


def main() -> None:
    display_banner()
    args = parse_args()
    if args.subcommand == 'init':
        init.init(args.target, args.template)
    elif args.subcommand == 'build':
        build.build(search_build_config(args), args.profile, args.proxy, args.network)
    elif args.subcommand == 'test':
        test.test(search_build_config(args), args.profile, nvidia=args.nvidia, network=args.network)
    elif args.subcommand == 'list':
        list_builds.list_builds(PESTO_WORKSPACE)


def search_build_config(args: Any) -> str:
    build_config_path = str(args.build_config)

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


if __name__ == "__main__":
    main()
