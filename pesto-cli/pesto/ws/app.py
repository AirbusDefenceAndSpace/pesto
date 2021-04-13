import sys
import uvicorn
from fastapi import FastAPI, APIRouter
from pesto.ws.v1 import v1
from pesto.version import PESTO_VERSION
from pydantic import BaseSettings

import logging
from loguru import logger
from loguru._defaults import LOGURU_FORMAT

_logging_format = '[%(asctime)s] %(process)d-%(levelname)s '
_logging_format += '%(module)s::%(funcName)s():l%(lineno)d: '
_logging_format += '%(message)s'

class InterceptHandler(logging.Handler):
    """
    Default handler from examples in loguru documentaion.
    See https://loguru.readthedocs.io/en/stable/overview.html#entirely-compatible-with-standard-logging
    """

    def emit(self, record):
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )

logging.basicConfig(handlers=[InterceptHandler()], level=0)
# Configure loguru logging
# Use LOGURU env variables to pimp the format 
## LOGURU_SERIALIZE=TRUE for JSON
logger.configure(
    handlers=[{"sink": sys.stdout}]
)
# Configure loguru also for uvicorn
logging.getLogger("uvicorn.access").handlers = [InterceptHandler()]

TIMEOUT = 1_000_000

class Settings(BaseSettings):
    app_name: str = "PESTO"
    app_api_version: str = "1.0.0"
    app_version: str = PESTO_VERSION
    contact_mail: str = "pesto@airbus.com"
    request_timeout: int = TIMEOUT
    response_timeout: int = TIMEOUT
    keep_alive_timeout: int = TIMEOUT

# Declare FastAPI application
app = FastAPI(
    title='App baked by PESTO from Airbus',
    description='This app is packaged with Airbus Processing Factory aka PESTO',
    version=PESTO_VERSION
)

app.include_router(v1)

def main():
    uvicorn.run(app, host="0.0.0.0", port=8080)    

if __name__ == '__main__':
    main()