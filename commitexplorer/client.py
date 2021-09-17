import json
import os
from appdirs import user_cache_dir

from requests import Response
from requests.adapters import HTTPAdapter
from requests_cache import CachedSession
from urllib3 import Retry
from typing import Dict, List, Union

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


BACKEND = 'squirrel'


def query_backend(url: str) -> Response:
    if BACKEND == 'squirrel':
        backend_url = 'http://squirrel.inf.unibz.it:8180'
    elif BACKEND == 'ironspeed':
        backend_url = 'http://10.10.20.160:8180'
    else:
        raise ValueError(f'Unknown backend: {BACKEND}')

    full_url = f"{backend_url}/ce/{url}"
    return http_session.get(full_url)


def _query_commit_explorer(url: str) -> Union[None, Dict, List]:
    try:
        response = query_backend(url)
    except Exception as e:
        raise CommitExplorerClientException("Error while sending request to CommitExplorer backend") from e
    if response.status_code != 200:
        raise CommitExplorerClientException(f"ClientExplorer backend returned error status code: {response.status_code}")
    else:
        return json.loads(response.text)


def query_collection(collection_name: str) -> List[str]:
    return _query_commit_explorer(f'query/{collection_name}')


def query_commit(sha: str, projection: Dict) -> Dict:
    return _query_commit_explorer(f'commit/{sha}')


