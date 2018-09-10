bc-events
=========

Python client for interfacing with the BriteEvents API

Installing
----------

This library is published to our internal pip wheelhouse. To install, simply include the following in your requirements file.

::

    --find-links http://bc-pip-wheelhouse.s3-website-us-east-1.amazonaws.com
    --trusted-host bc-pip-wheelhouse.s3-website-us-east-1.amazonaws.com

Then add ``bc-events==x.x`` as normal.

Usage
-----

If you are using this in a Django project, see django-britecore_

There are several abstraction layers that need to be initialized to publish an event.
These abstraction layers align well with web server requests. You should not have to create each layer for every web request.

First, you must create an ``EventClient``. In a web server context, this should be created once on startup.

.. code-block:: python

    from bc_events import EventClient

    event_client = EventClient(
        "https://api.mysite.britecore.com",
        "MyService",
        "path/to/topic_defitions.yaml"
    )


Next, you need an ``EventSession``. In a web server context, this should be created once per web request.
You can do this manually, but it is slightly easier to use the convenience methods on the client.

.. code-block:: python

    from .somewhere import event_client

    # Use a user_session when you have a cognito user id
    # Generally, the user id and job id will come from web request headers
    # In other contexts, they may come from sns topic attributes or some other event payload
    user_session = event_client.user_ession(
        "[COGNITO_USER_ID]",
        "[BC-JOB-ID]"
    )

    # Use a service_session when doing autmated tasks that do not originate from a user
    # If there is no origin context for a job id, generate your own
    service_session = event_client.service_session("[BC-JOB-ID]")


Once you have a session, you can then publish events.

.. code-block:: python

    from .elsewhere import user_session

    # Verbose publish call
    user_session.publish(
        action="Created",
        entity="MyEntity",
        data={"event": "json", "data": "here"}
    )

    # Shortcut "magic" calls with action_entity as the method
    user_session.created_my_entity({"event": "json", "data": "here"})

    # Flipping action and entity still works on "magic" calls
    user_session.my_entity_created({"event": "json", "data": "here"})


By default, your session will need to flush once the web request or other context completes successfully.

.. code-block:: python

    # After your session context executes successfully
    user_session.flush()


You can bypass the need for flushing by passing ``publish_immediately=True`` to the `EventSession`.
This is not reccommended in normal web request usage, as there is no way to rollback an event after it hits the API.


.. _django-britecore: https://github.com/IntuitiveWebSolutions/django-britecore
