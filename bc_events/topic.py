from .utils import build_topic_name


class Topic(object):
    def __init__(self, category, entity, action, schema):
        """Creates a new Topic

        Parameters
        ----------
        category : str
            Topic category
        entity : str
            Topic entity
        action : str
            Topic action
        schema : dict
            JSON schema to validate event payloads
        """
        self.category = category
        self.entity = entity
        self.action = action
        self.schema = schema

    @property
    def name(self):
        """Computed property to return this topic's name

        Returns
        -------
        str
            Unique name for this topic
        """

        return build_topic_name(self.category, self.entity, self.action)

    def __str__(self):
        return self.name

    def __repr__(self):
        return "Topic(category=%r, entity=%r, action=%r, schema=%r)" % (
            self.category,
            self.entity,
            self.action,
            self.schema,
        )
