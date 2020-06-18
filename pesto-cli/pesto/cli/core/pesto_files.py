from enum import Enum


class PestoFiles(Enum):
    description = 'api/description.json'
    input_schema = 'api/input_schema.json'
    output_schema = 'api/output_schema.json'
    config_schema = 'api/config_schema.json'
    config = 'api/config.json'
    version = 'api/version.json'
    service = 'api/service.json'

    build = 'build/build.json'
    requirements = 'build/requirements.json'

    @staticmethod
    def required():
        return set(PestoFiles).difference({
            PestoFiles.service,
            PestoFiles.build
        })
