import pytest

from bc_events.constants import ACTOR_TYPE_SERVICE, ACTOR_TYPE_THIRD_PARTY, ACTOR_TYPE_USER
from bc_events.utils import build_topic_name


def test_init(client, api_url, service_name):

    assert client.api_url == api_url
    assert client.service_name == service_name

    assert len(client.topic_table.keys()) == 3

    if api_url is not None:
        assert client.publish_url == api_url + "/events"


def test_user_session(user_id, job_id, user_session):

    assert user_session.actor_id == user_id
    assert user_session.job_id == job_id
    assert user_session.actor_type == ACTOR_TYPE_USER


def test_service_session(service_name, job_id, service_session):

    assert service_session.actor_id == service_name
    assert service_session.job_id == job_id
    assert service_session.actor_type == ACTOR_TYPE_SERVICE


def test_third_party_session(service_name, job_id, third_party_session):

    assert third_party_session.actor_id == service_name
    assert third_party_session.job_id == job_id
    assert third_party_session.actor_type == ACTOR_TYPE_THIRD_PARTY


def test_get_topic_found(client):
    for topic in client.topic_table.values():
        topic_match = client.get_topic(topic.category, topic.entity, topic.action)

        assert topic == topic_match


def test_get_topic_not_found(client):

    fake_category = "nope"
    fake_entity = "NotReal"
    fake_action = "Failed"
    fake_topic_name = build_topic_name(fake_category, fake_entity, fake_action)
    with pytest.raises(ValueError, match=fake_topic_name):
        client.get_topic(fake_category, fake_entity, fake_action)

