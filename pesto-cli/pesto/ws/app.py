import uvicorn
from fastapi import FastAPI, APIRouter
from pesto.ws.v1 import v1
from pesto.version import PESTO_VERSION
from pydantic import BaseSettings

import logging

_logging_format = '[%(asctime)s] %(process)d-%(levelname)s '
_logging_format += '%(module)s::%(funcName)s():l%(lineno)d: '
_logging_format += '%(message)s'

#logging.basicConfig(format=_logging_format, level=logging.DEBUG)
logging.basicConfig(format=_logging_format)

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