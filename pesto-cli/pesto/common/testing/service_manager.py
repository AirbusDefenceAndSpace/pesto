import subprocess
import time
from typing import Any

import docker
import docker.errors
import requests
from pesto.common.testing import logger


class ServiceManager:

    def __init__(
        self,
        docker_image: str,
        host_port: int = 4000,
        service_port: int = 8080,
        host_volume_path: str = None,
        image_volume_path: str = None,
        nvidia=False,
        attach_when_running=False,
        network: str = None,
    ):
        self.docker_image = docker_image
        self.host_port = host_port
        self.service_port = service_port
        self.host_volume_path = host_volume_path
        self.image_volume_path = image_volume_path
        self.nvidia = nvidia
        self.attach_when_running = attach_when_running
        if network is None:
            self.network = "bridge"
        else:
            self.network = network

        self._docker_client = docker.from_env()
        self._docker_container, self._existing_container = self._check_existing_container()

    def _check_existing_container(self):
        containers = self._docker_client.containers.list()
        for container in containers:
            ports = container.ports  # {'8080/tcp': [{'HostIp': '', 'HostPort': '4000'}]}
            tags = container.image.tags
            if self.docker_image in tags:
                for ports_dict in ports.get("{}/tcp".format(self.service_port), []):
                    if ports_dict.get("HostPort", "") == "{}".format(self.host_port):
                        logger.info("Already running container found {}".format(container.id))
                        return container, True

        return None, False

    @property
    def server_url(self):
        return "http://localhost:{}".format(self.host_port)

    @property
    def is_alive(self):
        try:
            response = requests.get("{}/api/v1/health".format(self.server_url))
            return response.status_code == 200
        except:
            return False

    def pull(self):
        try:
            self._docker_client.images.get(self.docker_image)
        except docker.errors.ImageNotFound:
            logger.info("Pulling {}".format(self.docker_image))
            self._docker_client.images.pull(self.docker_image)
            logger.info("Pulled image")
        except docker.errors.APIError:
            logger.info("Can't pull image {} you should have it in local other it will not work !".format(
                self.docker_image))

    def attach(self):
        if self._docker_container is not None:
            logger.info("Attaching in subprocess to container")
            cmd = "docker attach {}".format(self._docker_container.id)
            logger.info(cmd)
            subprocess.Popen(cmd, shell=True)
            time.sleep(5)

    def run(self):
        if self._docker_container is None and self.is_alive:
            logger.warning("There is a container running at {} but it does not match {}.\n"
                        "We assume that you know what you are doing".format(
                self.server_url, self.docker_image))
            return None

        if self._docker_container is None:
            self.pull()
            logger.info("Starting container with {} on port {}".format(self.docker_image, self.host_port))

            self._docker_container = self._docker_client.containers.run(
                self.docker_image,
                ports={self.service_port: self.host_port},
                detach=True,
                remove=True,
                runtime="nvidia" if self.nvidia else None,
                volumes={self.host_volume_path: {
                    "bind": self.image_volume_path,
                    "mode": "rw",
                }} if self.image_volume_path is not None and self.host_volume_path is not None else None
            )
            time.sleep(2)
            logger.info("Container {} started, available at {}".format(self._docker_container.id, self.server_url))

        # Healthcheck until service responds
        num_tries = 0
        max_tries = 10

        logger.info("Trying api/v1/health for {}st time".format(num_tries + 1))
        while (num_tries < max_tries) and (not self.is_alive):
            logger.info("Server not yet alive")
            num_tries += 1
            time.sleep(2)
            logger.info("Trying api/v1/health for {}th time".format(num_tries + 1))

        if num_tries < max_tries:
            logger.info("Server alive")
        else:
            logger.error("Timeout reached")

        # Attach
        if self.attach_when_running:
            self.attach()

        return self._docker_container.id

    def stop(self):
        if self._docker_container is not None:
            logger.info("Stopping container {}".format(self._docker_container.id))
            self._docker_container.stop()

    def __enter__(self) -> "ServiceManager":
        self.run()
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        if not self._existing_container:
            self.stop()
