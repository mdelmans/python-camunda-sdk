# Python Camunda SDK

## Roadmap

Outbound connectors
	[x] Base class
	[x] Connector config
    [...] Tests

Inbound connectors
	[x] Base class
	[x] Connector config
	[]  Activate inbound connector template
	[] Tests

Connection configs
	[x] Config from .env
	[x] Cloud connection
	[x] Local insecure connection
	[x]  Local secure connection 
	[] Tests

Template generation
	[x] Input mapping
	[x] Output mapping
	[] Type conersion Camunda <-> Python
	[] Tests

Documentation
	[x] Typehints
	[x] Dockstrings
	[] User's guide
	[] Examples

## Users guide

### Defining an outbound connector

```python
from typing import Literal
from pydantic import BaseModel, Field
from loguru import logger

from python_camunda_sdk import OutboundConnector


class StatusModel(BaseModel):
    status: Literal['ok', 'error']


class LogConnector(OutboundConnector):
    message: str = Field(description="Message to log")

    async def run(self, config) -> StatusModel:
        logger.info(f"LogConnector: {self.message}")

        return StatusModel(status='ok')

    class ConnectorConfig:
        name = "LogConnector"
        type = "log"
```

`StatusModel` is a return class for the connector. You don't have to use
it and can return a dictionary or a simple type (int, float, string, 
bool) instead.

`LogConnector` is an example connector class. Pydantic fields define
inputs the connector accepts. The names of the fields will be mapped to
the input names and description of the fields will be mapped to the
input labels.

`run` method is a main method that will be executed when a service task
is called. In this case, it just logs a message and returns a simple
status response.

`ConnectorConfig` is a subclass that must be defined for each connector
class and must specify name and type of the connector. Optionally, you
can also provide a timeout in seconds.

If you prefer, you can also use an `@outbound_connector` decorator
instead of `ConnectorConfig`.

```python
from python_camunda_sdk import outbound_connector

from pydantic import Field

@outbound_connector(
    name="LogConnector",
    type="log"
)
class LogConnector:
    message: str = Field(description="Message to log")

    async def run(self, config) -> StatusModel:
        logger.info(f"LogConnector: {self.message}")

        return StatusModel(status='ok')
```

### Setting up a runtime

Runtime expects the following environmental variables set:

`CAMUNDA_CONNECTION_TYPE`: Type of the connection. Can either be
	`CAMUNDA_CLOUD` for the SaaS version or `INSECURE` for an insecure
	self-hosted Zeebe server.

`ZEBEE_HOSTNAME`: Hostname for the self-hosted Zeebe server. Required
	only for the `INSECURE` connection type.

`ZEBEE_PORT`: Port for the self-hosted Zeebe server. Required only for
	the `INSECURE` connection type.

`CAMUNDA_CLUSTER_ID`: Clusted ID. Required only for the `CAMUNDA_CLOUD`
	connection type.

`CAMUNDA_CLIENT_ID`: Client ID. Required only for the `CAMUNDA_CLOUD`
	connection type.

`CAMUNDA_CLIENT_SECRET`: Client secret. Required only for the
	`CAMUNDA_CLOUD` connection type.


For convenience, you can define the environment variables in an `.env`
file.

### Starting the runtime

```python
from python_camunda_sdk import CamundaRuntime

runtime = CamundaRuntime(
    outbound_connectors=[LogConnector]
)

if __name__ == "__main__":
    runtime.start()
```

Simple as that.

### Defining an inbound connector


```python
import asyncio
import random
from python_camunda_sdk import InboundConnector


class RandomInbound(InboundConnector):
    async def loop(self):
        print('Random inbound in 2s')
        await asyncio.sleep(2)
        return {'random_number': random.randint(1, 100)}

    class ConnectorConfig:
        name = "random_inbound"
        cycle = 10
```
As with the outbound connectors, `ConnectorConfig` must be defined to
set up name and the cycle duration of the inboud connecor.

`loop()` method will be executed with an interval defined in the config
cycle (in seconds). It must return `None` if a message is not ready or
a BaseModel / dictionary when the message is ready to be publised to the
process.


Implementation of the inbound connectors differs from the one in the
official SDK. Instead of automatically fetching Intermediate Catch
Events from the `Operate` server, this version relies on a process
instance activating the inbound connector explicitly using an
`_activate_inbound_connector` service task passing the name and a
correlation key.

So your process might look something like:

--> [Activate random number generator] --> (Await random number) -->

Where [Activate connector] is a service task with:

type = `_activate_inbound_connector`

correlation_key = 'my_correlation_key'

name = 'random_inbound'

And await message is a Message Catch Intermediate Event with:

Message.name = 'random_inbound'
Message.correlation_key = 'my_correlation_key'

The runtime already knows about the `_activate_inbound_connector` task
and will activate the inbound connector with the matching name. When the
inbound connector returns a message, it will be associated with the
correlation_key provided in the task and published to Zebee.

To registed the inbound connector with the runtime just add it to the
list of connecors.

```python
from python_camunda_sdk import CamundaRuntime

runtime = CamundaRuntime(
    outbound_connectors=[RandomConnector],
    inbound_connector=[RandomInbound]
)

if __name__ == "__main__":
    runtime.start()
```


