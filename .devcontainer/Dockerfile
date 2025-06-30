FROM mcr.microsoft.com/devcontainers/python:3.12

ENV PYTHONUNBUFFERED=1

RUN apt-get update && \
    apt-get install -y curl
    
RUN apt-get install -y poppler-utils

RUN pip install --upgrade pip black flake8 isort
