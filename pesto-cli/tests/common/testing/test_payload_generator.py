import json

from pesto.common.testing.payload_generator import PayloadGenerator


def test_file_loader() -> None:
    loader = PayloadGenerator('file://')
    payload = loader.generate('resources/data/input')
    with open('resources/data_expected.json') as _:
        expected = json.load(_)

    assert payload.keys() == expected.keys()
    for k in payload:
        assert payload[k] == expected[k]

    assert json.dumps(payload, sort_keys=True, indent=4) == json.dumps(expected, sort_keys=True, indent=4)
