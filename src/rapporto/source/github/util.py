import logging
import os
import urllib.parse

import requests_cache

logger = logging.getLogger(__name__)


def repository_name(url: str, with_org: bool = False) -> str:
    """
    Compute GitHub repository name from full URL.

    https://github.com/tech-writing/rapporto
    https://github.com/tech-writing/rapporto/issues/19
    https://api.github.com/repos/tech-writing/rapporto
    """
    if "api.github.com" in url:
        url = url.replace("/repos", "")
    uri = urllib.parse.urlparse(url)
    parts = uri.path.split("/")
    if with_org:
        return parts[1] + "/" + parts[2]
    else:
        return parts[2]


class GitHubHttpClient:
    session = requests_cache.CachedSession(backend="sqlite", expire_after=3600)
    if "GH_TOKEN" in os.environ:
        session.headers.update({"Authorization": f"Bearer {os.getenv('GH_TOKEN')}"})
    else:
        logger.warning("GH_TOKEN not defined. This will exhaust the rate limit quickly.")
