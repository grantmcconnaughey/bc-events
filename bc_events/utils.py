import logging

import requests
from tenacity import Retrying, retry_if_exception_type, retry_if_result, stop_after_delay, wait_exponential

logger = logging.getLogger("bc.events")


def build_topic_name(category, entity, action):
    """Builds a topic name from it's parts

    Simply a standardized format for looking up and printing topics

    Parameters
    ----------
    category : str
        Topic category
    entity : str
        Topic entity
    action : str
        Topic action

    Returns
    -------
    str
        Formatted topic name
    """
    return "{category}.{entity}{action}".format(category=category, entity=entity, action=action)


class EventsApiRetryingWrapper(object):
    def __init__(self, url, payload, headers={}, delay=0.45, max_delay=5, max_time=35):
        self.url = url
        self.payload = payload
        self.headers = headers
        self.response = None
        self.errors_we_can_retry = ["ProvisionedThroughputExceededException", "InternalFailureException"]
        self.delay = delay
        self.max_delay = max_delay
        self.max_time = max_time

    def post(self):
        return requests.post(self.url, json=self.payload, headers=self.headers)

    def extract_failed_record(self, pair):
        record, result = pair
        if result in self.errors_we_can_retry:
            return record

    def retry_if_we_need_to(self, response):
        response_json = response.json()

        if response.status_code in [400, 500]:
            if response_json["errorType"] in self.errors_we_can_retry:
                # The API itself failed, retry the same payload
                logger.warning(f"Request failed. Retrying this request: {response_json}")
                return True

            # The API itself failed, but not with an error we should retry
            logger.warning(f"Unable to retry this request: {response_json}")
            return False

        if response_json.get("failedRecords", 0) == 0:
            # No failures, don't retry
            return False

        # There were partial failures, the payload to retry with should only contain failed records
        self.payload = [
            record
            for record in map(self.extract_failed_record, zip(self.payload, response_json["records"]))
            if record is not None
        ]

        logger.warning(f"Partial failures. Retrying {len(self.payload)} records.")
        return True

    def invoke(self):
        retryer = Retrying(
            retry=retry_if_exception_type(requests.exceptions.Timeout) |
                  retry_if_exception_type(requests.exceptions.ConnectionError) |
                  retry_if_result(self.retry_if_we_need_to),
            stop=stop_after_delay(self.max_time),
            wait=wait_exponential(multiplier=self.delay, max=self.max_delay),
        )
        return retryer(self.post)
