from pathlib import Path

from pesto.common.testing.test_runner import TestRunner

port = 4000
service = "{{cookiecutter.project_sname}}:{{cookiecutter.project_version}}"
# service = "{{cookiecutter.project_sname}}:{{cookiecutter.project_version}}-stateful" # test stateful profile
nvidia = "gpu" in service

test_dir = Path(__file__).parent

print("Running in {}".format(test_dir))

# Mimic Pesto Test
results = TestRunner(docker_image_name=service, nvidia=nvidia).run_all(test_dir / "resources")

ok_dict = {"NoDifference": True}


def test_describe():
    assert results.get("describe") == ok_dict


def test_processing():
    for test_key in results.keys():
        if "test_" in test_key:
            assert results.get(test_key) == ok_dict
