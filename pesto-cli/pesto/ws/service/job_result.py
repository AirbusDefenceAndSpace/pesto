import logging
import os
from enum import Enum
from typing import List, Tuple, Optional
import re
from pesto.common.utils import load_json
from pesto.ws.service.job_list import JobListService

log = logging.getLogger(__name__)


class ResultType(Enum):
    image = ['tif', 'png', 'jpg']
    file = ['string', 'float', 'int']
    json = ['json']

    @property
    def extensions(self):
        return self.value

    def transform(self, path: str) -> str:
        if self == ResultType.json:
            return load_json(path)
        if self == ResultType.file:
            with open(path, 'r') as f:
                return f.read()
        if self == ResultType.image:
            return path


class JobResultService:

    def __init__(self, url_root: str, job_id: str):
        self.job_id = job_id
        self.job_path = os.path.join(JobListService.PESTO_WORKSPACE, self.job_id)
        self.url_root = url_root

    def get_results(self) -> dict:
        result = {}
        for file in sorted(os.listdir(self.job_path)):
            name, ext = os.path.splitext(file)
            if re.search(r'\d+$', name) is not None:
                idx = re.search(r'\d+$', name).group()
                if name.endswith(idx):
                    new_name = name[:-len(idx)]
                    if result.get(new_name):
                        result[new_name].append('{}/api/v1/jobs/{}/results/{}'.format(self.url_root, self.job_id, name))
                    else:
                        result[new_name] = ['{}/api/v1/jobs/{}/results/{}'.format(self.url_root, self.job_id, name)]
            else:
                if name != '__response':
                    result[name] = '{}/api/v1/jobs/{}/results/{}'.format(self.url_root, self.job_id, name)

        return result

    def get_partial_result(self, result_id: str) -> Tuple[str, ResultType]:
        for data_type in ResultType:
            path = self._get_partial_result_path(data_type.extensions, result_id)
            if path is not None:
                output = data_type.transform(path)
                log.info('get job result {} : type={} output={}'.format(result_id, data_type, output))
                return output, data_type

        raise ValueError('No partial result found for job_id={} result_id={}'.format(self.job_id, result_id))

    def _get_partial_result_path(self, extensions: List[str], result_id: str) -> Optional[str]:
        for extension in extensions:
            path = os.path.join(self.job_path, result_id + '.' + extension)
            if os.path.exists(path):
                return path

        return None
