import logging
import os

log = logging.getLogger(__name__)


class JobListService(object):
    PESTO_WORKSPACE = '/tmp/.pesto/jobs'

    def __init__(self) -> None:
        self.PESTO_WORKSPACE = JobListService.PESTO_WORKSPACE

    def job_list(self, url_root: str) -> dict:
        log.info('job_list : url_root = {}'.format(url_root))

        result = {}

        if os.path.exists(self.PESTO_WORKSPACE):
            log.info('workspace found : {}'.format(self.PESTO_WORKSPACE))
            for job_id in os.listdir(self.PESTO_WORKSPACE):
                result[job_id] = {'link': '{}/api/v1/jobs/{}/status'.format(url_root, job_id)}
        return result
