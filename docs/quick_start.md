# Quick start

## Outbound connector

Outbound connectors are defined as classes derived from `OutboundConnector`. Bellow is a code of a simple connector that logs messages to console.

``` py linenums="1"
from pydantic import Field
from loguru import logger

from python_camunda_sdk import OutboundConnector


class LogConnector(OutboundConnector):
    message: str = Field(description="Message to log")

    async def run(self, config) -> str:
        logger.info(f"LogConnector: {self.message}")

        return self.message

    class ConnectorConfig:
        name = "LogConnector"
        type = "log"

```

Fields on the connector class define inputs to the connector.
!!! tip
	Using `Field` is optional but it is recommended to set `description` as it will be used for template generation.

The `ConnectorConfig` class defines the `name` of the connector and its `type`. Both must be specified are used to generate template.

Finally, the logic of the connector is defined in a `run` method. Make sure you annotate the return type.

!!! warning
	If `run` returns nothing, make sure you annotate it with `async def run(self, config) -> None`.