from typing import List, Type, Optional, Union

from grpc import ssl_channel_credentials

import asyncio

from pyzeebe import (
    ZeebeWorker,
    ZeebeClient,
    create_insecure_channel,
    create_camunda_cloud_channel,
    create_secure_channel
)

from loguru import logger

from python_camunda_sdk.connectors import (
    OutboundConnector,
    InboundConnector
)

from python_camunda_sdk.runtime.config import (
    ConnectionConfig,
    CloudConfig,
    SecureConfig,
    InsecureConfig,
    generate_config_from_env
)


class CamundaRuntime:
    """Creates a worker that listens to the service tasks for the specified
    outbound and inbound connectors.

    !!! tip
        If `config` is not supplied will attempt to
            generate from the environmental variables.

    Arguments:
        config: Connection config.
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

        self._inbound_connectors = inbound_connectors

    @logger.catch(message='Failed to connect to Zebee', reraise=True)
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

    @logger.catch(message='Failed to load connector')
    def _load_connector(
        self,
        connector_cls: Type[Union[OutboundConnector, InboundConnector]]
    ) -> None:
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
        task_wrapper(connector_cls.to_task(client=self._client))

    async def main(self):
        """Main asyncronous method of the runtime. Use it if you want to
        run the runtime inside your async loop.
        """
        self._connect()

        connectors = self._outbound_connectors + self._inbound_connectors

        for connector_cls in connectors:
            logger.info(
                f'Loading {connector_cls._config.name}'
                f' ({connector_cls._config.type})'
            )
            self._load_connector(connector_cls)

        logger.info('Starting runtime')
        await self._worker.work()

    def start(self):
        """Syncronous method to start the runtime. Will run in the main
        asycn loop.
        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.main())
