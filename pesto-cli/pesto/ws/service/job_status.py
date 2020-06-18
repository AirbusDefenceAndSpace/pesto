import os

from pesto.ws.service.job_list import JobListService


class JobStatusService:
    def __init__(self, url_root: str, job_id: str):
        self.job_id = job_id
        self.job_path = os.path.join(JobListService.PESTO_WORKSPACE, self.job_id)
        self.url_root = url_root

    def get_status(self) -> dict:
        if not os.path.exists(self.job_path):
            message = 'path does not exists : {}'.format(self.job_path)
            raise RuntimeError(message)
        if not os.listdir(self.job_path):
            return {
                'status': 'RUNNING',
                'progress': 0,
            }
        return {
            'status': 'DONE',
            'progress': 100,
            'link': '{}/api/v1/jobs/{}/results'.format(self.url_root, self.job_id)
        }
