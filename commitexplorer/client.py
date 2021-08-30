import json
import os
from appdirs import user_cache_dir

from requests import Response
from requests.adapters import HTTPAdapter
from requests_cache import CachedSession
from urllib3 import Retry
from typing import Optional


retry_strategy = Retry(total=10, backoff_factor=10)
http_adapter = HTTPAdapter(max_retries=retry_strategy)
if 'CACHE_DIR' in os.environ:
    cache_dir = os.environ['CACHE_DIR']
else:
    cache_dir = os.path.join(user_cache_dir('commit-explorer-client'), 'http_cache')
http_session = CachedSession(allowable_codes=(200, 404), cache_name=cache_dir)
http_session.mount("http://", http_adapter)


class CommitExplorerClientException(Exception):
    pass


class CommitNotFoundException(Exception):
    pass


def _query_commit_explorer_ironspeed(sha: str) -> Optional[Dict]:
    IRONSPEED_URL = "http://squirrel.inf.unibz.it:8180/ce"
    return http_session.get(f"{IRONSPEED_URL}/{sha}")


def query_commit_explorer(sha: str) -> Optional[Dict]:
    try:
        response = _query_commit_explorer_ironspeed(sha)
    except Exception as e:
        raise CommitExplorerClientException("Error while sending request to CommitExplorer backend") from e
    if response.status_code == 404:
        raise CommitNotFoundException(f"Commmit {sha} not found in CommitExplorer")
    elif response.status_code != 200:
        raise CommitExplorerClientException(f"ClientExplorer backend returned error status code: {response.status_code}")
    else:
        return json.loads(response.text)


