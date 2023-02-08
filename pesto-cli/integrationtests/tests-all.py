#!/usr/bin/env python3
import sys

import docker
import json
import os
import shutil
import tarfile
import tempfile
import time

import pkg_resources
from pesto.cli.app import ALGO_TEMPLATE_PATH
from pesto.cli.app import init, build, test
from pesto.cli.run import docker as pesto_docker
from pesto.common.testing.endpoint_manager import EndpointManager
from pesto.common.testing.service_manager import ServiceManager


sname = "algo-service"
version = "1.0.0.dev0"
image_name = "{}:{}".format(sname, version)
description = "Pesto Template contains all the boilerplate you need to create a processing-factory project"
organization = "pesto"
licence = "Property of pesto, all rights reserved"
email = "pesto@airbus.com"
payload = '{"image":"file:///opt/algo-service/pesto/tests/resources/test_1/input/image.png"}'
temp = os.path.join(tempfile.gettempdir(), 'pesto-it')


def check_init(use_legacy=False):
    print("--------------------------------")
    print("---- Testing `init` command ----")
    print("--------------------------------")
    if use_legacy:
        # open file
        file = tarfile.open(pkg_resources.resource_filename(__name__, "legacy-init.tgz"))
        file.extractall(temp)
        file.close()
    else:
        init(temp, ALGO_TEMPLATE_PATH, True)

    print("Algorithm stub created. Checking that all files are present.")
    with open(pkg_resources.resource_filename(__name__, "init-files.txt")) as f:
        for index, line in enumerate(f):
            file = os.path.join(temp, sname, line.strip())
            if not os.path.exists(file):
                print("Missing file! {}".format(file))
                print("!!!! `init` command test failed.")
                return False

    print("Checking that variable replacement is done.")
    all_variables_ok = True

    fd = os.path.join(temp, sname, "pesto", "api", "description.json")
    print("Checking {}".format(fd))
    with open(fd) as json_file:
        data = json.load(json_file)
        all_variables_ok &= check_variable(data, 'title', sname, fd)
        all_variables_ok &= check_variable(data, 'name', sname, fd)
        all_variables_ok &= check_variable(data, 'version', version, fd)
        all_variables_ok &= check_variable(data, 'description', description, fd)
        all_variables_ok &= check_variable(data, 'organization', organization, fd)
        all_variables_ok &= check_variable(data, 'email', email, fd)
        all_variables_ok &= check_variable(data, 'licence', licence, fd)

    fd = os.path.join(temp, sname, "pesto", "api", "version.json")
    print("Checking {}".format(fd))
    with open(fd) as json_file:
        data = json.load(json_file)
        all_variables_ok &= check_variable(data, 'version', version, fd)

    fd = os.path.join(temp, sname, "pesto", "build", "build.json")
    print("Checking {}".format(fd))
    with open(fd) as json_file:
        data = json.load(json_file)
        all_variables_ok &= check_variable(data, 'name', sname, fd)
        all_variables_ok &= check_variable(data, 'version', version, fd)

    if all_variables_ok:
        print(">>>> `init` command test successful.")
        return True
    else:
        print("!!!! `init` command test failed.")
        return False


def check_variable(data, variable, expected, file):
    if data[variable] != expected:
        print("{}[{}] is wrong: expected='{}' / actual='{}'".format(file, variable, expected, data[variable]))
        return False
    return True


def check_build(use_ssl=False):
    print("---------------------------------")
    print("---- Testing `build` command ----")
    print("---------------------------------")

    # Note: the default template generates a 1.2G image
    build(os.path.join(temp, sname, "pesto", "build", "build.json"),
          list(), None, None, "host")

    docker_client = docker.from_env()
    image = docker_client.images.get(image_name)
    if not image:
        print("!!!! `build` command test failed: Docker image '{}' NOT found.".format(image_name))
        return False

    with ServiceManager(docker_image=image_name, network="host", use_ssl=use_ssl) as service:
        service.run()
        time.sleep(5)
        describe = EndpointManager(server_url=service.server_url).describe
        if describe.get("title") == sname and describe.get("version") == "1.0.0.dev0":
            print(">>>> `build` command test successful: Docker image found and responding.")
            return True
        else:
            print("!!!! `build` command test failed: Docker image not exposing expected values.")
            return False


def check_run_docker(use_ssl=False):
    print("--------------------------------------")
    print("---- Testing `run docker` command ----")
    print("--------------------------------------")

    result_file = os.path.join(temp, "run_docker_output.txt")
    pesto_docker(payload, image_name, result_file, None, None, False, use_ssl, "host", True)
    if os.path.exists(result_file):
        with open(result_file) as json_file:
            data = json.load(json_file)
            if data.get('image') is not None:
                print(">>>> `run docker` command test successful: image found in output file.")
                return True
            else:
                print("!!!! `run docker` command test failed: no image found in output file found.")
                print(data)
                return False
    else:
        print("!!!! `run docker` command test failed: no output file found.")
        return False


def check_run_local(use_ssl=False):
    print("-------------------------------------")
    print("---- Testing `run local` command ----")
    print("-------------------------------------")

    result_file = os.path.join(temp, "run_local_output.txt")
    docker_client = docker.from_env()
    docker_client.containers.run(image_name,
                                 ["bash", "-c", "pesto run local '{}' {}".format(payload, result_file)],
                                 auto_remove=True,
                                 volumes=["{}:{}".format(temp, temp)],
                                 environment={"PESTO_USE_SSL": 'true' if use_ssl else 'false'})
    print("---- docker started ----")

    if os.path.exists(result_file):
        with open(result_file) as json_file:
            data = json.load(json_file)
            if data.get('image') is not None:
                print(">>>> `run local` command test successful: image found in output file.")
                return True
            else:
                print("!!!! `run docker` command test failed: no image found in output file found.")
                print(data)
                return False
    else:
        print("!!!! `run local` command test failed: no output file found.")
        return False


def check_test(use_ssl=False):
    print("--------------------------------")
    print("---- Testing `test` command ----")
    print("--------------------------------")
    test(os.path.join(temp, sname, "pesto", "build", "build.json"), list(), False, use_ssl, None)

    result_file = os.path.join(tempfile.gettempdir(), "pesto", "tests", "algo-service", "1.0.0.dev0", "results.json")
    if os.path.exists(result_file):
        with open(result_file) as json_file:
            result_data = json.load(json_file)
            expected_data = json.loads('{"describe":{"NoDifference": true},"test_1":{"NoDifference": true},"test_2":{"NoDifference": true}}')
            if result_data == expected_data:
                print(">>>> `test` command test successful: no differences detected.")
                return True
            else:
                print("!!!! `test` command test failed: differences found. Check results in {}.".format(result_file))
                return False
    else:
        print("!!!! `test` command test failed: no result file found.")
        return False


def rm_temp_dir():
    if os.path.exists(temp):
        shutil.rmtree(temp)


if __name__ == "__main__":
    rm_temp_dir()
    success = True

    try:
        print("==========================================")
        print("==== Testing legacy template with SSL ====")
        print("==========================================")
        success = success and check_init(True) and check_build(True) and check_run_docker(True) and check_run_local(True) and check_test()

        rm_temp_dir()

        print("=============================================")
        print("==== Testing legacy template without SSL ====")
        print("=============================================")
        success = success and check_init(True) and check_build() and check_run_docker() and check_run_local() and check_test()

        rm_temp_dir()

        print("=============================================")
        print("==== Testing generated template with SSL ====")
        print("=============================================")
        success = success and check_init() and check_build(True) and check_run_docker(True) and check_run_local(True) and check_test()

        rm_temp_dir()

        print("================================================")
        print("==== Testing generated template without SSL ====")
        print("================================================")
        success = success and check_init() and check_build() and check_run_docker() and check_run_local() and check_test()

    finally:
        rm_temp_dir()
        if success:
            print("****** ALL TESTS OK *******")
            sys.exit(0)
        else:
            print("!!!!!! A TEST FAILED, CHECK THE LOGS ABOVE !!!!!!")
            sys.exit(1)

