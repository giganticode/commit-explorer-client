from types import SimpleNamespace
from unittest import mock

from pytest import raises

from commitexplorer.client import query_commit_explorer, CommitNotFoundException, CommitExplorerClientException


@mock.patch("commitexplorer.client.http_session")
def test_query_commit_explorer_success(session_mock):
    session_mock.get.return_value = SimpleNamespace(status_code=200, text='{}')

    assert query_commit_explorer("any_sha") == {}


@mock.patch("commitexplorer.client.http_session")
def test_query_commit_explorer_404(session_mock):
    session_mock.get.return_value = SimpleNamespace(status_code=404, text='{}')

    with raises(CommitNotFoundException):
        query_commit_explorer("any_sha")


@mock.patch("commitexplorer.client.http_session")
def test_query_commit_explorer_403(session_mock):
    session_mock.get.return_value = SimpleNamespace(status_code=403, text='{}')

    with raises(CommitExplorerClientException):
        query_commit_explorer("any_sha")


@mock.patch("commitexplorer.client.http_session")
def test_query_commit_explorer_exception(session_mock):
    session_mock.get.side_effect = Exception()

    with raises(CommitExplorerClientException):
        query_commit_explorer("any_sha")
