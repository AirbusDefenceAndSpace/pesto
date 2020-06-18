import collections as collections_abc
import os
from typing import List, Any, Dict, Union

import six

from pesto.common.utils import load_json


class ProfileLoader(object):
    def __init__(self, root_path: str, profiles: List[str]):
        self.root_path = root_path
        self.profiles = profiles

    def load(self, filename: str) -> Any:
        full_path = os.path.join(self.root_path, filename)
        content = load_json(full_path)
        for profile in self.profiles:
            try:
                profile_content = load_json(profile_path(profile, full_path))
                content = _update(content, profile_content)
            except:
                pass
        return content


def profile_path(profile: str, path: str) -> Union[str, None]:
    new_path = '.{}'.format(profile).join(os.path.splitext(path))
    if profile is not None and os.path.exists(new_path):
        return new_path
    return None


def _update(d: Dict, u: Dict) -> Dict:
    for k, v in six.iteritems(u):
        dv = d.get(k, {})
        if not isinstance(dv, collections_abc.Mapping):
            d[k] = v
        elif isinstance(v, collections_abc.Mapping):
            d[k] = _update(dv, v)
        else:
            d[k] = v
    return d
