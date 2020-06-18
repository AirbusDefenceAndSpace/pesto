import logging
import os
from typing import Tuple, Any

from pesto.common.utils import save_json
from pesto.ws.core.match_apply import MatchApply, Json

log = logging.getLogger(__name__)


class JsonSerializer(MatchApply):
    def __init__(self, job_path: str):
        self.job_path = job_path

    def match(self, schema: Json):
        ref = schema.get('$ref')
        return ref in [
            '#/definitions/Metadata',
            '#/definitions/Metadatas',
            '#/definitions/Polygon',
            '#/definitions/Polygons'
        ]

    def convert(self, data: Tuple[Any, str]):
        payload, key = data
        filename = os.path.join(self.job_path, key + '.json')
        log.info('saving json : ' + filename)
        save_json(filename, payload)
