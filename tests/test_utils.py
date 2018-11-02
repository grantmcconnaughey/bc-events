from collections import namedtuple
from unittest.mock import Mock

import pytest
import requests

from bc_events.utils import EventsApiRetryingWrapper

single_event = {
    "action": "Create",
    "category": "testing",
    "entity": "TestEntity",
    "data": {"message": "BULK PASSED"},
    "actor": {"id": "bulk-pass-test", "type": "service"},
}

bulk_events = [single_event] * 4


class MultiResponse:

    def __init__(self, responses):
        self.responses = responses
        self.status_code = None

    def __getattribute__(self, key):
        if key in ["responses", "status_code"]:
            return super().__getattribute__(key)
        elif key == "json":
            response, status_code = self.responses.pop(0)
            self.status_code = status_code
            return lambda: response


def create_sample_response(response, status_code):
    return namedtuple("Struct", ["json", "status_code"])(lambda: response, status_code)


@pytest.fixture(
    params=[
        ("https://some_url.com/events/", single_event, {"x-britecore-job-id", "1234567"}),
        ("https://some_url.com/events/bulk/", bulk_events, {}),
    ]
)
def events_api_wrapper(request):
    params = request.param
    return EventsApiRetryingWrapper(params[0], params[1], params[2], delay=0.01, max_delay=0.1, max_time=1)


def test_post(events_api_wrapper, monkeypatch):
    post_mock = Mock()
    monkeypatch.setattr(requests, "post", post_mock)
    events_api_wrapper.post()
    assert post_mock.call_count in [1, 4]


def test_extract_failed_record(events_api_wrapper):

    # A successful result will be ignored
    sample1 = (single_event, "Success")
    result = events_api_wrapper.extract_failed_record(sample1)
    assert result is None

    # ProvisionedThroughputExceededException will be retried
    sample2 = (single_event, "ProvisionedThroughputExceededException")
    result = events_api_wrapper.extract_failed_record(sample2)
    assert result == single_event

    # InternalFailureException will be retried
    sample3 = (single_event, "InternalFailureException")
    result = events_api_wrapper.extract_failed_record(sample3)
    assert result == single_event

    # Anything else will not be retried
    sample4 = (single_event, "UnsupportedError")
    result = events_api_wrapper.extract_failed_record(sample4)
    assert result is None


def test_retry_if_we_need_to_on_400_provisioned_throughput_exceeded(events_api_wrapper):
    sample_response = create_sample_response({"errorType": "ProvisionedThroughputExceededException"}, 400)
    response = events_api_wrapper.retry_if_we_need_to(sample_response)

    # We need to retry this
    assert response is True


def test_retry_if_we_need_to_on_500_internal_failure(events_api_wrapper):
    sample_response = create_sample_response({"errorType": "InternalFailureException"}, 500)
    response = events_api_wrapper.retry_if_we_need_to(sample_response)

    # We need to retry this
    assert response is True


def test_retry_if_we_need_to_on_400_unsupported_failure(events_api_wrapper):
    sample_response = create_sample_response({"errorType": "SomethingWeCantRetryException"}, 400)
    response = events_api_wrapper.retry_if_we_need_to(sample_response)

    # We can't retry this
    assert response is False


def test_retry_if_we_need_to_on_all_events_succeeded(events_api_wrapper):
    sample_response = create_sample_response({"failedRecords": 0}, 201)
    response = events_api_wrapper.retry_if_we_need_to(sample_response)

    # We don't need to retry this
    assert response is False


def test_retry_if_we_need_to_on_partial_failure(events_api_wrapper):
    sample_response = create_sample_response({"failedRecords": 1, "records": [
            single_event,
            single_event,
            single_event,
            single_event,
            single_event,
        ]}, 201)
    response = events_api_wrapper.retry_if_we_need_to(sample_response)

    # We'll retry anything that needs to be retried
    assert response is True


def test_invoke_successful_call(events_api_wrapper, monkeypatch):
    requests_mock = Mock()
    requests_mock.return_value = create_sample_response({"failedRecords": 0, "records": [single_event]}, 201)
    monkeypatch.setattr(requests, "post", requests_mock)
    events_api_wrapper.invoke()
    assert requests_mock.call_count == 1


def test_invoke_with_bulk_retries(events_api_wrapper, monkeypatch):
    responses = [
        ({"failedRecords": 2, "records": ["Success", "ProvisionedThroughputExceededException", "InternalFailureException"]}, 201),
        ({"failedRecords": 2, "records": ["ProvisionedThroughputExceededException", "InternalFailureException"]}, 201),
        ({"failedRecords": 2, "records": ["ProvisionedThroughputExceededException", "InternalFailureException"]}, 201),
        ({"failedRecords": 0, "records": ["Success", "Success"]}, 201),
    ]
    requests_mock = Mock()
    requests_mock.return_value = MultiResponse(responses)
    monkeypatch.setattr(requests, "post", requests_mock)

    events_api_wrapper.invoke()
    assert requests_mock.call_count == 4


def test_invoke_without_bulk_retries(events_api_wrapper, monkeypatch):
    responses = [
        ({"failedRecords": 0, "records": ["Success", "Success"]}, 201)
    ]

    requests_mock = Mock()
    requests_mock.return_value = MultiResponse(responses)
    monkeypatch.setattr(requests, "post", requests_mock)

    events_api_wrapper.invoke()
    assert requests_mock.call_count == 1


def test_invoke_with_events_retries(events_api_wrapper, monkeypatch):
    responses = [
        ({"errorType": "ProvisionedThroughputExceededException"}, 400),
        ({"errorType": "InternalFailureException"}, 500),
        ({"errorType": "ProvisionedThroughputExceededException"}, 400),
        ({"eventId": "some_id", "jobId": "some_job"}, 201)
    ]

    requests_mock = Mock()
    requests_mock.return_value = MultiResponse(responses)
    monkeypatch.setattr(requests, "post", requests_mock)

    events_api_wrapper.invoke()
    assert requests_mock.call_count == 4


def test_invoke_without_events_retries(events_api_wrapper, monkeypatch):
    responses = [
        ({"eventId": "some_id", "jobId": "some_job"}, 201)
    ]

    requests_mock = Mock()
    requests_mock.return_value = MultiResponse(responses)
    monkeypatch.setattr(requests, "post", requests_mock)

    events_api_wrapper.invoke()
    assert requests_mock.call_count == 1