# inbound


Inbound connectors send messages to Zeebe.

Upon a call, an inbound connector will start an async task with a coroutine defined in a
`run` method and return `None` to Zeebe.

As soon as the async task completes, the connector will publish a
message with the predefined name and correlation key.


Example:
```py linenums="1"
--8<-- "sleep.py"
```

::: python_camunda_sdk.connectors.inbound