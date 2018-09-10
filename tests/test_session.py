from unittest.mock import Mock

import pytest

from bc_events import EventSession
from bc_events.constants import ACTOR_TYPE_SERVICE


@pytest.fixture
def immediate_session(client, service_name, job_id):
    return EventSession(service_name, ACTOR_TYPE_SERVICE, job_id, client, publish_immediately=True)


def test_publish_delayed(user_session, created_test_payload):
    user_session.publish(action="Created", entity="Test", data=created_test_payload)

    assert len(user_session.events) == 1

    event = user_session.events[0]

    assert event.data == created_test_payload


def test_publish_immediately(immediate_session, created_test_payload, requests_mock):

    immediate_session.publish(action="Created", entity="Test", data=created_test_payload)

    assert len(immediate_session.events) == 0

    if immediate_session.client.api_url:
        requests_mock.post.assert_called_once()


def test_publish_no_kwargs(user_session, created_test_payload):

    with pytest.raises(TypeError, match="keyword args"):
        user_session.publish("Created", "Test", created_test_payload)


def test_magic_call(user_session, created_test_payload):
    user_session.created_test(created_test_payload)

    assert len(user_session.events) == 1

    event = user_session.events[0]

    assert event.data == created_test_payload


def test_magic_call_flipped(user_session, created_test_payload):
    user_session.test_created(created_test_payload)

    assert len(user_session.events) == 1

    event = user_session.events[0]

    assert event.data == created_test_payload


def test_magic_call_incorrect(user_session, created_test_payload):

    with pytest.raises(AttributeError, match="tested_create"):
        user_session.tested_create(created_test_payload)


def test_flush(user_session):

    fake_event = Mock()
    another_fake_event = Mock()

    user_session.events = [fake_event, another_fake_event]

    user_session.flush()

    fake_event.publish.assert_called_once()
    another_fake_event.publish.assert_called_once()
