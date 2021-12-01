import sys
import json
import os

from uvicorn import Config, Server
from fastapi import FastAPI, APIRouter
from pesto.ws.v1 import v1
from pesto.version import PESTO_VERSION
from pesto.ws.config import settings

import logging
from loguru import logger
from datetime import datetime


## Some words on logging
# Logging in PESTO is highly customizable and based on Loguru
# There is 2 way of logging : 
#     * Log in text format on standard output
#     * Log serialized in JSON with custom fields
# Env var PESTO_LOG_SERIALIZE=TRUE activate the JSON serialization
# Env var PESTO_LOG_FORMAT='str' give the mapping for serialization
# For example : 'date:application_date,message:application_message,level:application_severity' map date from log record in a field name application_date etc...
# When the application is started, all log handlers are removed and replaced by the InterceptHandler below to ensure all logs are handle by loguru

def log_mapping(conf:str):
    """
    Split str of log format into a dict
    Example : date:application_date,message:application_message is split in : 
    {'date':'application_date','message':'application_message'}
    """
    mapping = dict()
    for i in conf.split(','):
        mapping[i.split(':')[0]] = i.split(':')[1]
    return mapping

def sink(message):
    """
    Custom sink function for serialization
    """
    # If we are here, log_serialize is True, check format is specified
    if settings.log_format is not None:
        mapping = log_mapping(settings.log_format)
        serialized = json.loads(message)
        simplified = dict()
        for k in mapping.keys():
            if k != 'level' and k !='time':
                simplified[mapping[k]] = serialized['record'][k]
            elif k != 'time':
                simplified[mapping[k]] = serialized['record']['level']['name']
            else:
                simplified[mapping[k]] = datetime.utcfromtimestamp(serialized['record']['time']['timestamp']).strftime('%Y-%m-%dT%H:%M:%S:%fZ')

        # Add extra key which don't correspond to record first level of information
        for k in serialized['record']['extra']:
            simplified[k] = serialized['record']['extra'][k]
        print(simplified, flush=True)
    else:
        print(message,flush=True)

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

def setup_logging():
    logging.root.handlers = [InterceptHandler()]
    logging.root.setLevel(level=settings.log_level)
    for name in logging.root.manager.loggerDict.keys():
        logging.getLogger(name).handlers = []
        logging.getLogger(name).propagate = True
    if settings.log_serialize:
        log_extra = None
        if settings.log_extra is not None:
            log_extra = json.loads(settings.log_extra)
        logger.configure(handlers=[{"sink": sink, "serialize": True}], extra=log_extra)
    else:
        logger.configure(handlers=[{"sink": sys.stdout}])

app = FastAPI(
    title='App baked by PESTO from Airbus',
    description='This app is packaged with Airbus Processing Factory aka PESTO',
    version=PESTO_VERSION
)

app.include_router(v1)

def main():
    server = Server(Config(app,host="0.0.0.0",port=8080))
    setup_logging()
    server.run()   

if __name__ == '__main__':
    main()