import filecmp
import json
import os
from tempfile import NamedTemporaryFile
from typing import Any

import jsonschema
# TODO: fix this import (should not import anything from ws)
from pesto.ws.features.converter.image.image import Image


def mkdir(path: str) -> None:
    directory = os.path.dirname(path)
    if not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)


def load_json(path: str, filename: str = None) -> Any:
    if filename is not None:
        path = os.path.join(path, filename)
    with open(path) as file:
        json_content = json.load(file)
    return json_content


def validate_json(dictionary: dict, schema: dict) -> dict:
    jsonschema.validate(dictionary, schema)
    return dictionary


def save_json(path: str, item: Any) -> str:
    os.makedirs(os.path.dirname(path), exist_ok=True)

    with open(path, 'w') as outfile:
        json.dump(item, outfile, indent=2, sort_keys=True)
    return path


def truncate_dict_for_debug(d: dict, max_size=80):
    dd = dict()
    for k in d:
        val = d[k]
        if isinstance(val, dict):
            dd[k] = truncate_dict_for_debug(val)
        elif isinstance(val, str):
            dd[k] = val[:max_size] + ("..." if len(d[k]) > max_size else "")
        elif isinstance(val, list):
            dd[k] = [(v[:max_size] + ("..." if len(d[k]) > max_size else "") if isinstance(v, str) else v) for v in val]
        else:
            dd[k] = val

    return dd


def compare_dicts(expected: dict, actual: dict) -> dict:
    def _is_file(val):
        return isinstance(val, str) and (os.path.exists(val) or os.path.exists(val.replace("file://", "")))

    def _is_image(name: str) -> bool:
        return name.endswith(".tif") or name.endswith(".jpg") or name.endswith(".png")

    def _compare_vals(expected_v: Any, actual_v: Any) -> bool:

        if _is_file(expected_v) and _is_file(actual_v):
            expected_path = expected_v.replace("file://", "")
            response_path = actual_v.replace("file://", "")
            return filecmp.cmp(response_path, expected_path)
        elif (not _is_file(actual_v)) and (_is_file(expected_v) and _is_image(expected_v)):
            response_path = "{}{}".format(NamedTemporaryFile().name, os.path.splitext(expected_v)[1])
            response_path = Image.from_base64(actual_v).to_path(response_path)
            response_path = response_path.replace("file://", "")
            expected_path = expected_v.replace("file://", "")
            return filecmp.cmp(response_path, expected_path)
        elif isinstance(expected_v, list):
            return all([any([_compare_vals(v1, v2) for v2 in actual_v]) for v1 in expected_v])
        else:
            return expected_v == actual_v

    expected_keys = set(expected.keys())
    actual_keys = set(actual.keys())
    shared_keys = expected_keys.intersection(actual_keys)

    added = list(actual_keys - shared_keys)
    removed = list(expected_keys - shared_keys)

    modified = dict()

    for o in shared_keys:
        exp_v, actual_v = expected[o], actual[o]
        if isinstance(exp_v, dict) and isinstance(actual_v, dict):
            if not exp_v == actual_v:
                _cmp = compare_dicts(exp_v, actual_v)
                if _cmp is not None:
                    modified[o] = _cmp
        elif not _compare_vals(exp_v, actual_v):
            modified[o] = {
                "actual": actual_v,
                "expected": exp_v
            }

    comparison = dict()

    if len(added) > 0:
        comparison["KeysNotExpected"] = added
    if len(removed) > 0:
        comparison["KeysMissing"] = removed
    if len(modified.keys()) > 0:
        comparison["KeysNotEqual"] = modified
    if len(comparison.keys()) == 0:
        return None

    return comparison
