#!/usr/bin/python3

import argparse
from pathlib import Path
import json

from pesto.common.testing.service_manager import ServiceManager

port = 4000
service = "{{cookiecutter.project_sname}}:{{cookiecutter.project_version}}"

parser = argparse.ArgumentParser(description="""Start the PESTO webservice.
Example: """ + __file__ + """ [-p gpu]
""", formatter_class=argparse.RawTextHelpFormatter)
    
parser.add_argument('-p', '--profile', nargs='+', default="", help='List of profiles to apply. Use stateless to enable the asynchronous service')
args = parser.parse_args()

if len(args.profile):
    service = service + "-" + "-".join(args.profile)

nvidia = "gpu" in service
print("Launching service " + service)

with ServiceManager(docker_image=service, host_port=port, nvidia=nvidia) as service:
    input("Press Enter to quit ...")

