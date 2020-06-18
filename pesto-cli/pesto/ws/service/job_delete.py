import logging
import os
import shutil

from pesto.ws.service.job_list import JobListService

log = logging.getLogger(__name__)


class JobDeleteService:
    def __init__(self, url_root: str, job_id: str):
        self.job_id = job_id
        self.job_path = os.path.join(JobListService.PESTO_WORKSPACE, self.job_id)
        self.url_root = url_root

    def delete(self) -> None:
        log.info('delete: job_id = {}'.format(self.job_id))
        shutil.rmtree(self.job_path)

    def delete_partial(self, result_id: str) -> None:
        for ext in [
            'json',
            'tif', 'jpeg', 'png',
            'float', 'int', 'string'
        ]:
            _remove_silent(os.path.join(self.job_path, result_id + '.' + ext))


def _remove_silent(path: str) -> None:
    try:
        os.remove(path)
    except:
        pass
