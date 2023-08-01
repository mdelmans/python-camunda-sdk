import inspect

from typing import Union, Optional
from collections.abc import Coroutine

from loguru import logger

from pydantic import BaseModel
from pydantic import ValidationError

from pyzeebe import Job, ZeebeClient

from python_camunda_sdk.config import OutboundConnectorConfig
from python_camunda_sdk.meta import ConnectorMetaclass, Connector
from python_camunda_sdk.types import SimpleTypes


class OutboundConnector(Connector, base_config_cls=OutboundConnectorConfig):
    """Outbound connector

    Base class for outbound connectors.
    """
    @classmethod
    def to_task(
        cls,
        client: ZeebeClient
    ) -> Coroutine[..., Optional[Union[BaseModel, SimpleTypes]]]:
        """Converts connector class into a pyzeebe task function.

        Returns:
            A function that validates arguments and executes the connector logic.
        """
        async def task(job: Job, **kwargs) -> Union[BaseModel, SimpleTypes]:
            try:
                connector = cls(**kwargs)
            except ValidationError as e:
                logger.exception(
                    'Failed to validate arguments for '
                    f'{cls._config.name}'
                )
                raise e

            ret = await connector.execute(job=job)
            return ret
        return task
