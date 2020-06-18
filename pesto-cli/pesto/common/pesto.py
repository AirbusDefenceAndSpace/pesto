import os
from pathlib import Path

PESTO_WORKSPACE = os.environ.get('PESTO_WORKSPACE', '{}/.pesto'.format(Path.home()))
_PESTO_PROFILE = os.environ.get('PESTO_PROFILE', '')


class Pesto:
    @staticmethod
    def get_profile():
        return _PESTO_PROFILE

    @staticmethod
    def is_profile_active(profile: str) -> bool:
        return profile in _PESTO_PROFILE
