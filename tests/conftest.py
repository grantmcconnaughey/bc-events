from unittest.mock import Mock

import pytest
import requests
import yaml

from bc_events import EventClient
from bc_events.utils import EventsApiRetryingWrapper


@pytest.fixture(params=["https://fake-site.britecore.com", None])
def api_url(request):
    return request.param


@pytest.fixture
def service_name():
    return "BcEventsUnitTests"


@pytest.fixture(params=[0, 1, 2])
def topic_definitions(request):
    topic_definitions_path = "tests/test_events.yaml"

    if request.param == 0:
        return topic_definitions_path

    topic_definitions_file = open(topic_definitions_path)

    request.addfinalizer(topic_definitions_file.close)

    if request.param == 1:
        return topic_definitions_file

    return yaml.load(topic_definitions_file)


@pytest.fixture
def client(api_url, service_name, topic_definitions):
    return EventClient(api_url, service_name, topic_definitions)


@pytest.fixture
def user_id():
    return "USER_ID"


@pytest.fixture
def job_id():
    return "JOB_ID"


@pytest.fixture
def user_session(client, user_id, job_id):
    return client.user_session(user_id, job_id)


@pytest.fixture
def service_session(client, job_id):
    return client.service_session(job_id)


@pytest.fixture
def third_party_session(client, job_id):
    return client.third_party_session(job_id)


@pytest.fixture
def created_test_payload():
    return {"id": "MyTestId", "url": "https://somewhere.com/tests/MyTestId"}


@pytest.fixture
def events_api_wrapper_invoke_mock(monkeypatch):
    mock = Mock()
    monkeypatch.setattr(EventsApiRetryingWrapper, "invoke", mock)
    return mock


@pytest.fixture
def post_mock(monkeypatch):
    from collections import namedtuple

    post_mock = Mock()
    post_mock.return_value = namedtuple("Struct", ["json", "status_code"])(lambda: {}, 201)
    monkeypatch.setattr(requests, "post", post_mock)
    return post_mock
