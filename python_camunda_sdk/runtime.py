import os

from typing import List, Type, Literal, Optional

from grpc import ssl_channel_credentials

from pydantic import BaseModel, Field

import asyncio

from pyzeebe import (
    ZeebeWorker,
    ZeebeClient,
    create_insecure_channel,
    create_camunda_cloud_channel,
    create_secure_channel
)

from loguru import logger

from python_camunda_sdk import (
    ConnectionConfig,
    OutboundConnector,
    InboundConnector,
    CloudConfig,
    SecureConfig,
    InsecureConfig,
    generate_config_from_env
)


class CamundaRuntime:
    """Camunda runtime.

    Creates worker that listens to the service tasks for the specified
    outbound connectors and manages creation of the inbound connector
    instances.

    Args:
        outbound_connectors: A list of outbound connector classes.
        inbound_connectors: A list of the inbound connector classes.

    """
    def __init__(
        self,
        config: Optional[ConnectionConfig] = None,
        outbound_connectors: List[Type[OutboundConnector]] = [],
        inbound_connectors: List[Type[InboundConnector]] = []
    ):

        if config is None:
            self._config = generate_config_from_env()
        else:
            self._config = config

        self._outbound_connectors = outbound_connectors

        self._inbound_connectors = {}

        for connector_cls in inbound_connectors:
            self._inbound_connectors[connector_cls._config.name] = connector_cls

    @logger.catch(message="Failed to connect to Zebee", reraise=True)
    def _connect(self):
        if isinstance(self._config, CloudConfig):
            channel = create_camunda_cloud_channel(
                **self._config.dict()
            )
        elif isinstance(self._config, InsecureConfig):
            channel = create_insecure_channel(
                **self._config.dict()
            )
        elif isinstance(self._config, SecureConfig):
            channel = create_secure_channel(
                hostname=self._config.hostname,
                port=self._config.port,
                channel_credentials=ssl_channel_credentials(
                    root_certificates=self._config.root_certificates,
                    private_key=self._config.private_key,
                    certificate_chain=self._config.certificate_chain
                )
            )
        else:
            raise TypeError(f'Unsupported config type {type(self._config)}')
        
        self._worker = ZeebeWorker(channel)
        self._client = ZeebeClient(channel)

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
        ret = await connector.loop()

        if isinstance(ret, BaseModel):
            ret = ret.dict()
        elif not isinstance(ret, dict):
            raise TypeError(
                f'Inbound connector {connector.__class__.__name__}'
                f'({connector._config.name})'
                f' returned an invalid value type ({ret.__class__}).'
                f'BaseModel or dict were expected.'
            )
        await self._client.publish_message(
            name=connector._config.name,
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
        self._connect()

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
