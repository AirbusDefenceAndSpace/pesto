class ProcessingError(Exception):

    def __init__(self, message: str) -> None:
        self.message = message

    def __repr__(self) -> str:
        return 'ProcessingError: {}'.format(self.message)
