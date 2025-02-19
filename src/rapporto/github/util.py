import urllib.parse
from pathlib import Path


def repository_name(url: str, with_org: bool = False) -> str:
    uri = urllib.parse.urlparse(url)
    path = Path(uri.path)
    if with_org:
        return path.parent.name + "/" + path.name
    else:
        return path.name
