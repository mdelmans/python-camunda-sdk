# Define an outbound connector

Outbound connectors are defined as classes derived from `OutboundConnector`. Bellow is a code of a simple connector that logs messages to console and returns a `StatusModel` object.

!!! tip
    Connectors don't have to return a `BaseModel`. `dict` or simple types like `str`, `int` or `float` work as well.

``` py linenums="1" title="log.py"
--8<-- "log.py"
```

Fields on the connector class define inputs to the connector.
!!! tip
	Using `Field` is optional but it is recommended to set `description` as it will be used for template generation.

The `ConnectorConfig` class defines the `name` of the connector and its `type`. Both must be specified are used to generate template.

Finally, the logic of the connector is defined in a `run` method. Make sure you annotate the return type.

!!! warning
	If `run` returns nothing, make sure you annotate it with `async def run(self, config) -> None`.