from kwargs_only import kwargs_only

from .event import Event


class EventSession(object):
    def __init__(self, actor_id, actor_type, job_id, client, publish_immediately=False):
        """Creates a new EventSession

        Parameters
        ----------
        object : [type]
            [description]
        actor_id : str
            ID for the session's actor
        actor_type : str
            Type of the session's actor
        job_id : str
            Correlation ID for linking requests across services
        client : EventClient
            EventClient that knows about our service name, api url, and topic definitions
        publish_immediately : bool, optional
            Indicates whether events should be published as soon as `publish` is called,
            or if they should be queued and flushed.
            (the default is False, which requires a `flush` before events are truly published)
        """
        self.actor_id = actor_id
        self.actor_type = actor_type
        self.job_id = job_id
        self.client = client

        self.publish_immediately = publish_immediately
        self.events = []

    def __repr__(self):
        return "EventSession(actor_id=%r, actor_type=%r, job_id=%r, client=%r, publish_immediately=%r)" % (
            self.actor_id,
            self.actor_type,
            self.job_id,
            self.client,
            self.publish_immediately,
        )

    def flush(self):
        """Flushes events from the queue to the API

        This allows us to build up events over a session and only send them
        if the session's context is successful.
        If the context fails for any reason, and flush is not called,
        will not send events and don't have to worry about rolling them back.
        """

        # TODO use a bulk api endpoint once it exists
        for event in self.events:
            event.publish()

    def _publish(self, topic, data):
        """Internal method for publishing data to a topic

        Parameters
        ----------
        topic : Topic
            The Topic object to which we will publish this event
        data : dict
            The data payload for the event
        """

        event = Event(topic=topic, data=data, session=self)

        if self.publish_immediately:
            event.publish()
        else:
            self.events.append(event)

    @kwargs_only
    def publish(self, action=None, entity=None, data=None, category=None):
        """Primary publication method

        Verbose method to specify all parts of a topic and the data to publish to it.

        Note
        ----
        You must use kwargs to call this method. This simply makes the various
        arguments clearer and lets you not worry about the order in which they are provided.
        It will also allow us to tweak the call signature in the future without breaking your calls.

        Parameters
        ----------
        action : str
            Topic action
        entity : str
            Topic entity
        data : dict
            Event payload to publish to the topic
        category : str, optional
            Topic category (the default is None, which will use the default category on the client)
        """

        category = category or self.client.default_category
        topic = self.client.get_topic(category, entity, action)
        self._publish(topic, data)

    def __getattr__(self, attr_name):
        """Magic handler to allow shortcuts to the `publish` method

        This only works when using the default category.
        If a category override is needed, use `publish` directly.

        Parameters
        ----------
        attr_name : str
            The shortcut method call that we will turn into a topic action and entity.

        Raises
        ------
        ValueError
            If we cannot parse the attr and find a corresponding topic

        Returns
        -------
        function
            A wrapped call to `publish` that only accepts the event payload data
        """

        def build_entity_action_pair(entity_parts, action):
            entity = "".join([part.capitalize() for part in entity_parts])
            return entity, action.capitalize()

        attr_parts = attr_name.split("_")

        entity, action = build_entity_action_pair(attr_parts[:-1], attr_parts[-1])
        try:
            topic = self.client.get_topic(self.client.default_category, entity, action)
        except ValueError:
            entity, action = build_entity_action_pair(attr_parts[1:], attr_parts[0])
            try:
                topic = self.client.get_topic(self.client.default_category, entity, action)
            except ValueError:
                raise ValueError("Could not resolve convenience wrapper for: " + attr_name)

        def publish_wrapper(data):
            self._publish(topic, data)

        return publish_wrapper

