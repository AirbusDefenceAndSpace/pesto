import logging
import os
from typing import Any

from pesto.common.utils import load_json

log = logging.getLogger(__name__)


class DescribeService(object):
    SERVICE_JSON_PATH = '/etc/pesto/service.json'
    VERSION_CONTENT_PATH = '/etc/pesto/version.json'

    def __init__(self, url_root: str):
        self.description = load_json(DescribeService.SERVICE_JSON_PATH)
        self.url_root = url_root

    @staticmethod
    def compute_version() -> Any:
        return load_json(DescribeService.VERSION_CONTENT_PATH)

    def compute_describe(self) -> dict:
        describe = {
            _: self.description[_] for _ in {
                'title',
                'name',
                'version',
                'family',
                'description',
                'organization',
                'email',
                'resources',
                'asynchronous'
            }
        }

        if 'batched' in self.description:
            describe['batched'] = self.description['batched']

        describe.update({
            _: self.description[_] for _ in self.description.keys() & {
                'keywords',
                'template',
                'config'
            }
        })

        describe.update({
            'input': self._build_io_schema('input'),
            'output': self._build_io_schema('output'),
            '_links': {
                'self': {
                    'relation': 'Access to describe resource',
                    'href': self._compute_endpoint('describe'),
                    'type': 'application/json',
                    'method': 'GET'
                },
                'execution': {
                    'relation': 'Processing resource',
                    'href': self._compute_endpoint('process'),
                    'type': self._compute_execution_type(),
                    'method': 'POST'
                },
                'config': {
                    'relation': 'Processing configuration',
                    'href': self._compute_endpoint('config'),
                    'type': 'application/json',
                    'method': 'GET'
                },
                'version': {
                    'relation': 'Processing version',
                    'href': self._compute_endpoint('version'),
                    'type': 'application/json',
                    'method': 'GET'
                },
                'health': {
                    'relation': 'Processing health',
                    'href': self._compute_endpoint('health'),
                    'type': 'text/plain',
                    'method': 'GET'
                }

                # metrics
                ## TODO TO BE IMPLEMENTED

                # icon
                ## TODO Unimplemented

                # license
                ## TODO TO BE IMPLEMENTED

                # documentation
                ## TODO TO BE IMPLEMENTED
                ## Maybe return the swagger UI
            }
        })

        return describe

    def _compute_endpoint(self, name: str) -> str:
        return os.path.join(self.url_root, 'api', 'v1', name)

    def _compute_execution_type(self) -> str:
        if isinstance(self.description['output'].get('content'), str):
            return self.description['output'].get('content')
        return 'Complex type, see output in describe content for more information'

    def _build_io_schema(self, field: str) -> dict:
        properties = self.description[field]

        required = properties.pop('required', [])
        definition = properties.pop('definition', {})
        schema = properties.pop('$schema', 'http://json-schema.org/draft-06/schema#')
        title = properties.pop('title', '')
        type = properties.pop('type', "object")
        content = properties.pop('content', None)
        definitions = properties.pop('definitions', {})
        description = properties.pop('description', "Expected format")
        if 'properties' in properties:
            properties = properties['properties']

        result = {
            "$schema": schema,
            "title": title,
            "type": type,
            "description": description,
            "definition": definition,
            "definitions": definitions,
            "properties": properties
        }
        if required:
            result['required'] = required
        if content:
            result['content'] = content

        return result
