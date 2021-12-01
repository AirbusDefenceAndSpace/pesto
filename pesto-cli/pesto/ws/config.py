import os
from pydantic import BaseSettings
from pesto.version import PESTO_VERSION

TIMEOUT = 1_000_000

class Settings(BaseSettings):
    app_name: str = "PESTO"
    app_api_version: str = "1.0.0"
    app_version: str = PESTO_VERSION
    contact_mail: str = "pesto@airbus.com"
    request_timeout: int = TIMEOUT
    response_timeout: int = TIMEOUT
    keep_alive_timeout: int = TIMEOUT
    log_serialize: bool = (os.environ['PESTO_LOG_SERIALIZE'] == 'TRUE') if 'PESTO_LOG_SERIALIZE' in os.environ.keys() else False
    log_format: str = os.environ['PESTO_LOG_FORMAT'] if 'PESTO_LOG_FORMAT' in os.environ.keys() else None
    log_level: str = os.environ['PESTO_LOG_LEVEL'] if 'PESTO_LOG_LEVEL' in os.environ.keys() else 'INFO'
    log_extra: str = os.environ['PESTO_LOG_EXTRA'] if 'PESTO_LOG_EXTRA' in os.environ.keys() else None

settings = Settings()