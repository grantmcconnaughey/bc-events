import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


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


def requests_session():
    """For use on AWS APIs that periodically fail with 500 and suggest retrying"""

    session = requests.Session()
    retry = Retry(total=3, read=3, connect=3, status_forcelist=[500], backoff_factor=0.3, method_whitelist=False)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session
