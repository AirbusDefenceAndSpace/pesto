from cookiecutter.main import cookiecutter

from pesto.cli.core.utils import PESTO_LOG


def init(target, template):
    cmd = "cookiecutter {} --output-dir {}".format(template, target)
    PESTO_LOG.info(cmd)
    PESTO_LOG.info("\nPlease fill necessary information to initialize your template\n")
    res = cookiecutter(template, output_dir=target)
    PESTO_LOG.info("Service generated at {}".format(res))
