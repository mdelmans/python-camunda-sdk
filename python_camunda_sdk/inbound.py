from typing import Optional, Union, Dict
import asyncio

from pydantic import BaseModel

from python_camunda_sdk.meta import ConnectorMetaclass
from python_camunda_sdk.config import InboundConnectorConfig

class InboundConnectorMetaclass(ConnectorMetaclass):
    _base_config_cls = InboundConnectorConfig

class InboundConnector(BaseModel, metaclass=InboundConnectorMetaclass):
    """Inbound connector base class.

    Attrs:
        correlation_key: Correlation key for the receive message event.
    """
    correlation_key: str

    # async def run(self) -> Optional[Union[BaseModel, Dict]]:
    #     """Virtual method for catching external event.

    #     Returns:
    #         None: if event has not been received in the current loop.
    #         Union[BaseModel, Dict]: if event has been received.
    #             The return value contains variables that will be passed
    #             to the process instance.
    #     """
    #     raise NotImplementedError

    async def loop(self) -> Union[BaseModel, Dict]:
        """Starts inbound connector loop.

        Repeats the `loop` method until a non-None value is returned
            with a period defined in a config (cycle).

        Returns:
            Content of the inbound message.
        """
        ret = None
        while ret is None:
            ret = await self.run()
            if ret is None:
                await asyncio.sleep(self._config.cycle_duration)
        return ret
