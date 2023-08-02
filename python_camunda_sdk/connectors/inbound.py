"""
Inbound connectors that send messages to Zeebe.

Upon execution will start an async task with a coroutine defined in a
`run` method and return `None` to Zeebe.

As soon as the async task completes, the connector will publish a
message with the defined name and correlation key.

Example:
    ```py
    import asyncio

    from pydantic import Field

    from python_camunda_sdk import InboundConnector


    class SleepConnector(InboundConnector):
        duration: int = Field(description="Duration of sleep in seconds")

        async def run(self, config) -> bool:
            await asyncio.sleep(self.duration)
            return True

        class ConnectorConfig:
            name = "Sleep"
            type = 'sleep'
    ```
"""
from typing import Union, Optional
from collections.abc import Coroutine
import asyncio

from loguru import logger

from pyzeebe import Job, ZeebeClient

from pydantic import BaseModel, ValidationError

from python_camunda_sdk.connectors.config import InboundConnectorConfig
from python_camunda_sdk.connectors import Connector
from python_camunda_sdk.types import SimpleTypes


class InboundConnector(Connector, base_config_cls=InboundConnectorConfig):
    """Inbound connector base class.
    """
    async def execute(
        self,
        job: Job,
        client: ZeebeClient,
        correlation_key: str,
        message_name: str
    ):
        variables = await super().execute(job=job)
        await client.publish_message(
            name=message_name,
            correlation_key=correlation_key,
            variables=variables
        )

    @classmethod
    def to_task(
        cls,
        client: ZeebeClient
    ) -> Coroutine[..., Optional[Union[BaseModel, SimpleTypes]]]:
        """Converts connector class into a pyzeebe task function.

        Returns:
            A coroutine that validates arguments and executes the connector
                logic.
        """
        async def task(
            job: Job,
            correlation_key: str,
            message_name: str,
            **kwargs
        ) -> Union[BaseModel, SimpleTypes]:
            try:
                connector = cls(
                    correlation_key=correlation_key,
                    **kwargs
                )
            except ValidationError as e:
                logger.exception(
                    'Failed to validate arguments for '
                    f'{cls._config.name}'
                )
                raise e

            loop = asyncio.get_event_loop()
            loop.create_task(
                connector._execute(
                    job=job,
                    client=client,
                    correlation_key=correlation_key,
                    message_name=message_name
                )
            )

        return task
