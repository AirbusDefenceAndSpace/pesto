import logging
import os
from typing import Tuple, Any

from pesto.common.utils import mkdir
from pesto.ws.core.match_apply import MatchApply, Json

log = logging.getLogger(__name__)


class StringSerializer(MatchApply):
    def __init__(self, job_path: str):
        self.job_path = job_path

    def match(self, schema: Json):
        return schema.get('type') == 'string'

    def convert(self, data: Tuple[Any, str]):
        payload, key = data
        filename = os.path.join(self.job_path, key + '.string')
        mkdir(filename)
        with open(filename, 'w') as outfile:
            outfile.write(str(payload))
