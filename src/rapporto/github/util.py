import logging
import os
import urllib.parse
from pathlib import Path

import requests_cache

logger = logging.getLogger(__name__)


def repository_name(url: str, with_org: bool = False) -> str:
    uri = urllib.parse.urlparse(url)
    path = Path(uri.path)
    if with_org:
        return path.parent.name + "/" + path.name
    else:
        return path.name


class GitHubHttpClient:
    session = requests_cache.CachedSession(backend="sqlite", expire_after=3600)
    if "GH_TOKEN" in os.environ:
        session.headers.update({"Authorization": f"Bearer {os.getenv('GH_TOKEN')}"})
    else:
        logger.warning("GH_TOKEN not defined. This will exhaust the rate limit quickly.")
