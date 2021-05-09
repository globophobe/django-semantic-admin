import os
from pathlib import Path


def set_secrets():
    directory = Path(__file__).resolve().parent
    with open(directory / "demo/settings/secrets.py", "r") as secrets:
        for line in secrets:
            key, value = line.split(" = ")
            os.environ[key] = value.strip()
