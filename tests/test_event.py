import pytest
from jsonschema import ValidationError
import time


@pytest.fixture
def event(user_session, created_test_payload):
    user_session.created_test(created_test_payload)

    return user_session.events[0]


def test_publish(event, job_id, requests_session_mock):
    event.publish()
    if event.session.client.api_url:
        requests_session_mock.post.assert_called_once_with(
            event.session.client.publish_url, json=event.request_json, headers={"x-britecore-job-id": job_id}
        )
    else:
        requests_session_mock.post.assert_not_called()


def test_data_validation_failure(event):

    event.data = {"bad": "payload"}

    with pytest.raises(ValidationError, match="'id' is a required property"):
        event.publish()


def test_json_validation_failure(event):

    event.topic.category = 5

    with pytest.raises(ValidationError, match="5 is not of type 'string") as err:
        event.publish()
