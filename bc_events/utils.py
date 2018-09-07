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
