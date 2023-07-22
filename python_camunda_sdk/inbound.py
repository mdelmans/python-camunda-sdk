from typing import Optional, Union, Dict, Coroutine
import asyncio

from loguru import logger

from pyzeebe import Job, ZeebeClient

from pydantic import BaseModel, ValidationError

from python_camunda_sdk.meta import ConnectorMetaclass
from python_camunda_sdk.config import InboundConnectorConfig
from python_camunda_sdk.types import SimpleTypes

class InboundConnectorMetaclass(ConnectorMetaclass):
    _base_config_cls = InboundConnectorConfig

class InboundConnector(BaseModel, metaclass=InboundConnectorMetaclass):
    """Inbound connector base class.
    """

    async def loop(self) -> Union[BaseModel, Dict]:
        """Starts inbound connector loop.

        Repeats the `loop` method until a non-None value is returned
            with a period defined in a config (cycle).

        Returns:
            Content of the inbound message.
        """
        ret = None
        while ret is None:
            ret = await self.run(config=self._config)
            if ret is None:
                await asyncio.sleep(self._config.cycle_duration)
        return ret

    async def execute(self,
        job: Job,
        client: ZeebeClient,
        correlation_key: str,
        message_name: str
    ):
        ret = await self.loop()
        if isinstance(ret, BaseModel):
            ret = ret.dict()

        return_variable_name = job.custom_headers.get(
            'resultVariable', None
        )
        variables = {}

        if return_variable_name is not None:
            return_value = None
            
            if isinstance(ret, BaseModel):
                return_value = ret.dict()
            else:
                return_value = ret

            variables = {return_variable_name: return_value}

        await client.publish_message(
            name=message_name,
            correlation_key=correlation_key,
            variables=variables
        )

    @classmethod
    def to_task(
        cls,
        client: ZeebeClient):
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
                connector.execute(
                    job=job,
                    client=client,
                    correlation_key=correlation_key,
                    message_name=message_name
                )
            )

        return task
