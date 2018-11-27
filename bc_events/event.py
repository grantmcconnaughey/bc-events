import logging

import jsonschema

from .constants import EVENT_SCHEMA
from .utils import EventsApiRetryingWrapper

logger = logging.getLogger("bc.events")


class Event(object):
    def __init__(self, topic, data, session):
        """Creates a new Event

        Parameters
        ----------
        topic : Topic
            A topic object that this event will publish to
        data : dict
            The data specific to this event. Should match topic's schema
        session : EventSession
            The event session that knows about the actor and job for this event
        """
        self.topic = topic
        self.data = data
        self.session = session

    @property
    def request_json(self):
        """Computed property that returns the JSON for use on the API

        Returns
        -------
        dict
            The json dict to be published to the API
        """

        return {
            "action": self.topic.action,
            "category": self.topic.category,
            "entity": self.topic.entity,
            "data": self.data,
            "actor": {"id": self.session.actor_id, "type": self.session.actor_type},
        }

    def __str__(self):
        return str(self.topic)

    def __repr__(self):
        return "Event(topic=%r, data=%r, session=%r)" % (self.topic, self.data, self.session)

    def validate(self):
        """Validates this event

        Raises
        ------
        jsonschema.ValidationError
            If the request json or event data do not validate against their schemas
        """

        jsonschema.validate(self.request_json, EVENT_SCHEMA)
        jsonschema.validate(self.data, self.topic.schema)

    def publish(self):
        """Publishes this event to the API if it is valid

        If no url has been set on the client, we assume local development, and only log the event.
        We validate the event before sending it to catch schema mismatch in development.
        """

        self.validate()

        request_json = self.request_json
        logger.info("Publishing event {}".format(self), extra={"context": request_json})

        # TODO this is going to need authentication when BriteAuth is hooked up to the API
        if self.session.client.publish_url:
            headers = {"x-britecore-job-id": self.session.job_id}
            events_api = EventsApiRetryingWrapper(self.session.client.publish_url, request_json, headers=headers)
            events_api.invoke()
