FROM ubuntu:18.04

ARG DOCKERDIR

RUN apt update && apt install -y \
    build-essential python3-pip twine git

RUN apt update && apt install -y \
    docker.io nano

ADD . /tmp

ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

RUN cd tmp && make all
