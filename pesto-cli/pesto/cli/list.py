import os

from pesto.cli.core.utils import PESTO_LOG


def list_builds(workspace_root):
    PESTO_LOG.info('Processing Factory repository path :'.format(workspace_root))
    PESTO_LOG.info('list of available builds :')

    for name in os.listdir(workspace_root):
        if name.startswith('.'):
            continue
        for version in os.listdir(os.path.join(workspace_root, name)):
            id = '{}:{}'.format(name, version)
            PESTO_LOG.info(''' {0} :
            pesto build {0}
             '''.format(id))
