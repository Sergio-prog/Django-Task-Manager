import os

from dotenv import load_dotenv

load_dotenv()


def get_env_key(key: str, _type: type = str):
    return _type(os.getenv(key))
