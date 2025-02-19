import urllib.parse
from pathlib import Path


def repository_name(url: str) -> str:
    uri = urllib.parse.urlparse(url)
    return Path(uri.path).name
