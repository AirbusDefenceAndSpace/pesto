import logging
import os

_logging_format = '[%(asctime)s] %(process)d-%(levelname)s '
_logging_format += '%(module)s::%(funcName)s():l%(lineno)d:\n'
_logging_format += '%(message)s'

logging.basicConfig(format=_logging_format, level=os.environ.get("PESTO_LOGLEVEL") or "INFO")

PESTO_LOG = logging.getLogger("pesto")
