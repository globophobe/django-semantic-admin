import os
from pathlib import Path


def set_secrets():
    directory = Path(__file__).resolve().parent
    with open(directory / "secrets.yaml", "r") as secrets:
        for line in secrets:
            key, value = line.split(": ")
            os.environ[key] = value.strip()


def docker_secrets():
    directory = Path(__file__).resolve().parent
    with open(directory / "secrets.yaml", "r") as secrets:
        build_args = []
        for line in secrets:
            key, value = line.split(": ")
            v = value.strip()
            build_args.append(f"{key}={v}")
        return "--build_args ".join(build_args)
