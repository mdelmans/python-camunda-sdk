from typing import Optional, Union, Dict
import asyncio

from pydantic import BaseModel

from python_camunda_sdk.meta import ConnectorMetaclass
from python_camunda_sdk.config import InboundConnectorConfig


class InboundConnectorMetaclass(ConnectorMetaclass):
    _base_class = InboundConnectorConfig


class InboundConnector(BaseModel, metaclass=InboundConnectorMetaclass):
    """Inbound connector base class.

    Attrs:
        correlation_key: Correlation key for the receive message event.
    """
    correlation_key: str

    async def loop(self) -> Optional[Union[BaseModel, Dict]]:
        """Virtual method for catching external event.

        Returns:
            None: if event has not been received in the current loop.
            Union[BaseModel, Dict]: if event has been received.
                The return value contains variables that will be passed
                to the process instance.
        """
        raise NotImplementedError

    async def run(self) -> Union[BaseModel, Dict]:
        """Stars inbound connector loop.

        Repeats the `loop` method until a non-None value is returned
            with a period defined in a config (cycle).

        Returns:
            Content of the inbound message.
        """
        ret = None
        while ret is None:
            ret = await self.loop()
            await asyncio.sleep(self._config.cycle)
        return ret
