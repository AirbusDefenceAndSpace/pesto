import os

class RemoteServiceManager:
    """
    Context manager class to temporarily set the PESTO_REMOTE_SERVICE_URL environment variable.
    """
    def __init__(self):
        self.original_url = None

    def __enter__(self):
        self.original_url = os.environ.get("PESTO_REMOTE_SERVICE_URL")
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass

    @property
    def server_url(self):
        return self.original_url
