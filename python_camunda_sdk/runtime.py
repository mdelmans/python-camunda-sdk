import os
import sys

from typing import List, Type

from pydantic import BaseModel, ValidationError

import asyncio

from pyzeebe import (
    ZeebeWorker,
    ZeebeClient,
    create_insecure_channel,
    create_camunda_cloud_channel
    )
from pyzeebe import Job

from loguru import logger

from dotenv import load_dotenv

from python_camunda_sdk import OutboundConnector, InboundConnector

CAMUNDA_CONNECTION_TYPE = 'CAMUNDA_CONNECTION_TYPE'
CAMUNDA_CLIENT_ID = 'CAMUNDA_CLIENT_ID'
CAMUNDA_CLIENT_SECRET = 'CAMUNDA_CLIENT_SECRET'
CAMUNDA_CLUSTER_ID = 'CAMUNDA_CLUSTER_ID'
ZEBEE_HOSTNAME = 'ZEBEE_HOSTNAME'
ZEBEE_PORT = 'ZEBEE_PORT'


class CamundaRuntime:
    """Camunda runtime.

    Creates worker that listens to the service tasks for the specified
    outbound connectors and manages creation of the inbound connector
    instances.

    Args:
        outbound_connectors: A list of outbound connector classes.
        inbound_connectors: A list of the inbound connector classes.

    """
    @logger.catch(onerror=lambda _: sys.exit(1))
    def __init__(
        self,
        outbound_connectors: List[Type[OutboundConnector]] = [],
        inbound_connectors: List[Type[InboundConnector]] = []
    ):
        load_dotenv()

        connection_type = os.environ.get(CAMUNDA_CONNECTION_TYPE, None)

        match connection_type:
            case "CAMUNDA_CLOUD":
                logger.info('Establising connection to Camunda cloud')
                channel = create_camunda_cloud_channel(
                    client_id=os.environ.get(
                        CAMUNDA_CLIENT_ID,
                        None
                    ),
                    client_secret=os.environ.get(
                        CAMUNDA_CLIENT_SECRET,
                        None
                    ),
                    cluster_id=os.environ.get(
                        CAMUNDA_CLUSTER_ID,
                        None
                    )
                )
            case "INSECURE":
                logger.info('Establishing an insecure channel to zebee')
                channel = create_insecure_channel(
                    hostname=os.environ.get(
                        ZEBEE_HOSTNAME,
                        None
                    ),
                    port=os.environ.get(
                        ZEBEE_PORT,
                        None
                    )
                )
            case None:
                raise ValueError('CAMUNDA_CONNECTION_TYPE varriable must be set')

            case _:
                raise ValueError('Unsupported CAMUNDA_CONNECTION_TYPE')

        self._worker = ZeebeWorker(channel)

        self._client = ZeebeClient(channel)

        self._outbound_connectors = outbound_connectors

        self._inbound_connectors = {}

        for connector_cls in inbound_connectors:
            self._inbound_connectors[connector_cls._name] = connector_cls

    @logger.catch(message="Failed to load connector")
    def _load_connector(self, connector_cls: Type[OutboundConnector]) -> None:
        """Loads a connector class and registers it with a pyzeebe worker.

        Args:
            connector_cls: Outbound connector class.
        """
        config = connector_cls._config

        task_wrapper = self._worker.task(
            task_type=config.type,
            timeout_ms=config.timeout*1000,
            before=[],
            after=[]
        )
        task_wrapper(connector_cls.to_task())

    async def _publish_inbound_message(
            self,
            connector: InboundConnector
    ) -> None:
        """Awaits for inbound connector to receive a message and
        publishes the results to zeebe.

        Raises:
            TypeError: If connector returns invalid message type. Only
                `BaseModel` and `Dict` are allowed.
        """
        ret = await connector.run()

        if isinstance(ret, BaseModel):
            ret = ret.dict()
        elif not isinstance(ret, dict):
            raise TypeError(
                f'Inbound connector {connector.__class__.__name__}'
                f'({connector._name})'
                f' returned an invalid value type ({ret.__class__}).'
                f'BaseModel or dict were expected.'
            )
        await self._client.publish_message(
            name=connector._name,
            correlation_key=connector.correlation_key,
            variables=ret
        )

    async def _activate_inbound_connector(
        self,
        name: str,
        correlation_key: str, **data
    ) -> None:
        """A worker method that activates the inbound connector.

        To activate an inbound connector process must call a service
        task of type '_acivate_inbound_connector' passing the name and
        the correlation key.

        Args:
            name: Name of the inbound connector.
            correlation_key: Correlation key for the inbound connector.

        Raises:
            ValueError: If an inbound connector with the given name is
                not registered with the runtime.
        """
        connector_cls = self._inbound_connectors.get(name, None)

        if connector_cls is None:
            raise ValueError(f'Unknown inbound connector: {name}')

        connector = connector_cls(
            name=name,
            correlation_key=correlation_key,
            **data
        )
        loop = asyncio.get_event_loop()
        loop.create_task(self._publish_inbound_message(connector))

    async def main(self):
        """Main asyncronous method of the runtime.
        """
        for connector_cls in self._outbound_connectors:
            logger.info(f'Loading {connector_cls._config.name} ({connector_cls._config.type})')
            self._load_connector(connector_cls)

        if len(self._inbound_connectors) > 0:
            logger.info('Starting inbound connector task')
            self._worker.task(
                task_type='_activate_inbound_connector'
            )(self._activate_inbound_connector)

        logger.info("Staring runtime")
        await self._worker.work()

    def start(self):
        """Syncronous method to start the runtime.
        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.main())
