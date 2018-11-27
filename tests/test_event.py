import pytest
from jsonschema import ValidationError


@pytest.fixture
def event(user_session, created_test_payload):
    user_session.created_test(created_test_payload)

    return user_session.events[0]


def test_publish(event, job_id, post_mock):
    event.publish()
    if event.session.client.api_url:
        post_mock.assert_called_once_with(
            event.session.client.publish_url, json=event.request_json, headers={"x-britecore-job-id": job_id}
        )
    else:
        post_mock.assert_not_called()


def test_str(event):
    assert str(event) == "testing.TestCreated"


def test_data_validation_failure(event):

    event.data = {"bad": "payload"}

    with pytest.raises(ValidationError, match="'id' is a required property"):
        event.publish()


def test_json_validation_failure(event):

    event.topic.category = 5

    with pytest.raises(ValidationError, match="5 is not of type 'string") as err:
        event.publish()
