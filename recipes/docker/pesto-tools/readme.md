# Simple docker image to build PESTO

This docker image is used to build pesto tools from a clean ubuntu environment. You can start with this docker image if you don't want to alter your host OS.

From the root of the project, simply call `./recipes/docker/build.sh -f ./recipes/docker/pesto-tools/Dockerfile`

You can now test PESTO from this image (it is setup for docker-in-docker) : 

* `docker run -it --net=host --rm -v /tmp:/tmp -v /var/run/docker.sock:/var/run/docker.sock pesto-tools`

Note : the volume /tmp is required for tests, as docker-in-docker uses host path to mount volumes.
