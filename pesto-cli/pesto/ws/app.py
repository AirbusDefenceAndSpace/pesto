from sanic import Sanic
from sanic_openapi import swagger_blueprint, openapi_blueprint

from pesto.ws.v1 import v1

import logging

_logging_format = '[%(asctime)s] %(process)d-%(levelname)s '
_logging_format += '%(module)s::%(funcName)s():l%(lineno)d: '
_logging_format += '%(message)s'

#logging.basicConfig(format=_logging_format, level=logging.DEBUG)
logging.basicConfig(format=_logging_format)

# Declare Sanic application
app = Sanic(__name__)

# API Configuration
app.blueprint(openapi_blueprint)
app.blueprint(swagger_blueprint)
app.blueprint(v1)

app.config.API_VERSION = '1.0.0'
app.config.API_TITLE = 'GeoProcessing SDK API'
app.config.API_DESCRIPTION = 'GeoProcessing SDK API'
app.config.API_TERMS_OF_SERVICE = 'Apache 2.0'
app.config.API_PRODUCES_CONTENT_TYPES = ['application/json', 'mimetypes/jpeg', 'mimetypes/tiff']
app.config.API_CONTACT_EMAIL = 'tbd@airbus.com'

app.config.KEEP_ALIVE = False

TIMEOUT = 1_000_000
app.config.REQUEST_TIMEOUT = TIMEOUT
app.config.RESPONSE_TIMEOUT = TIMEOUT
app.config.KEEP_ALIVE_TIMEOUT = TIMEOUT


def main():
    app.run(host="0.0.0.0", port=8080, debug=False)


if __name__ == '__main__':
    main()
