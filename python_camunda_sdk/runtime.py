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

from python_camunda_sdk import OutboundConnector, InboundConnector

CAMUNDA_CONNECTION_TYPE = 'CAMUNDA_CONNECTION_TYPE'
CAMUNDA_CLIENT_ID = 'CAMUNDA_CLIENT_ID'
CAMUNDA_CLIENT_SECRET = 'CAMUNDA_CLIENT_SECRET'
CAMUNDA_CLUSTER_ID = 'CAMUNDA_CLUSTER_ID'
ZEBEE_HOSTNAME = 'ZEBEE_HOSTNAME'
ZEBEE_PORT = 'ZEBEE_PORT'


class ConnectionConfig(BaseModel):
    connection_type: Literal['CAMUNDA_CLOUD', 'INSECURE', 'SECURE'] = Field(
        env_var="CAMUNDA_CONNECTION_TYPE", export=False
    )

class CloudConfig(ConnectionConfig):
    client_id: str = Field(env_var="CAMUNDA_CLIENT_ID")
    client_secret: str = Field(env_var="CAMUNDA_CLIENT_SECRET")
    cluster_id: str = Field(env_var="CAMUNDA_CLIENT_SECRET")

class InsecureConfig(ConnectionConfig):
    hostname: str = Field(env_var="ZEBEE_HOSTNAME")
    port: str = Field(env_var="ZEBEE_PORT")

class SSLConfig(BaseModel):
    root_certificates: str = Field(env_var="SSL_ROOT_CA")
    private_key: str = Field(env_var="SSL_PRIVATE_KEY")
    certificate_chain: Optional[str] = Field(env_var="SSL_CERTIFICATE_CHAIN")

class SecureConfig(InsecureConfig):
    ssl_config: SSLConfig


def get_env_var(key: str, strict: bool = False) -> str:
    value = os.environ.get(key, None)
    if value is None and strict:
        raise KeyError(f'Could not find environment variable {key}')

    return value

@logger.catch(message="Failed to load config variables", reraise=True)
def generate_config_from_env()->ConnectionConfig:
    cls_map = {
        "SECURE": SecureConfig,
        "INSECURE": InsecureConfig,
        "CAMUNDA_CLOUD": CloudConfig
    }

    connection_type = os.environ.get(CAMUNDA_CONNECTION_TYPE, None)
    if connection_type is None:
        raise ValueError('CAMUNDA_CONNECTION_TYPE is not defined')
    
    config_cls = cls.cls_map.get(connection_type, None)

    if config_cls is None:
        raise ValueError(
            'Unknown CAMUNDA_CONNECTION_TYPE ({connection_type})'
        )

    data = {}
    for field_name, field in cls.fields_:
        breakpoint()
    return config_cls(data)

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
        config: Optional[ConnectionConfig],
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

        self._worker = ZeebeWorker(channel)
        self._client = ZeebeClient(channel)

    # @logger.catch(message="Failed to establish connection", reraise=True)
    # def load_connection_config(self):
    #     config = generate_config()
        # connection_type = os.environ.get(CAMUNDA_CONNECTION_TYPE, None)

        # if connection_type == 'CAMUNDA_CLOUD':
        #     logger.info('Establising connection to Camunda cloud')
        #     channel = create_camunda_cloud_channel(
        #         client_id=get_env_var(
        #             CAMUNDA_CLIENT_ID,
        #             strict=True
        #         ),
        #         client_secret=get_env_var(
        #             CAMUNDA_CLIENT_SECRET,
        #             strict=True
        #         ),
        #         cluster_id=get_env_var(
        #             CAMUNDA_CLUSTER_ID,
        #             strict=True
        #         )
        #     )
        # elif connection_type == 'INSECURE':
        #     logger.info('Establishing an insecure channel to zeebe')
        #     channel = create_insecure_channel(
        #         hostname=get_env_var(
        #             ZEBEE_HOSTNAME
        #         ),
        #         port=get_env_var(
        #             ZEBEE_PORT
        #         )
        #     )
        # elif connection_type == 'SECURE':
        #     logger.info('Establishing a secure channel to zeebe')
        #     channel = create_secure_channel(
        #         hostname=get_env_var(
        #             ZEBEE_HOSTNAME
        #         ),
        #         port=get_env_var(
        #             ZEBEE_PORT
        #         ),
        #         channel_credentials=ssl_channel_credentials(
        #             root_certificates=get_env_var(
        #                 'SSL_ROOT_CA'
        #             ),
        #             private_key=get_env_var(
        #                 'SSL_PRIVATE_KEY'
        #             ),
        #             certificate_chain=get_env_var(
        #                 'SSL_CERTIFICATE_CHAIN'
        #             )
        #         )
        #     )
        # else:
        #     raise ValueError('Unsupported CAMUNDA_CONNECTION_TYPE')

        # return channel

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
