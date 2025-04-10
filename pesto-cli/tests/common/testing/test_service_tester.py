from pesto.common.testing.service_tester import ServiceTester
import pytest

@pytest.fixture
def service_tester():
    return ServiceTester(server_url="http://testserver.com")

def test_update_hrefs(service_tester):
    input_data = {
        "key1": "value1",
        "href": "http://localhost:4000/resource",
        "nested": {
            "href": "http://localhost:4000/another-resource",
            "list": [
                {"href": "http://localhost:4000/list-item-1"},
                {"key": "value"}
            ]
        }
    }

    expected_data = {
        "key1": "value1",
        "href": "http://testserver.com/resource",
        "nested": {
            "href": "http://testserver.com/another-resource",
            "list": [
                {"href": "http://testserver.com/list-item-1"},
                {"key": "value"}
            ]
        }
    }

    service_tester.update_hrefs(input_data)
    assert input_data == expected_data
