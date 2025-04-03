FROM mcr.microsoft.com/devcontainers/python:3.9

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-pip \
    twine \
    git \
    && apt-get clean

    RUN pip install pytest