import os
from typing import Optional
from pydantic import BaseModel, Field

from loguru import logger

class ConnectorConfig(BaseModel):
    """Base configuration class for connectors.
    
    !!! warning
        Should not be used dirrectly. For reference only.

    Attributes:
        name: Name of the connector.
        type: Type of the connector. This will correspond to the type of
            the service task that will be calling the connector.
        timeout: Timeout for the connector.
    """
    name: str
    type: str
    timeout: Optional[int] = 10

class OutboundConnectorConfig(ConnectorConfig):
    pass

class InboundConnectorConfig(ConnectorConfig):
    pass 

class ConnectionConfig(BaseModel):
    pass

class CloudConfig(ConnectionConfig):
    client_id: str = Field(env_var='CAMUNDA_CLIENT_ID')
    client_secret: str = Field(env_var='CAMUNDA_CLIENT_SECRET')
    cluster_id: str = Field(env_var='CAMUNDA_CLUSTER_ID')

class InsecureConfig(ConnectionConfig):
    hostname: str = Field(env_var='ZEBEE_HOSTNAME')
    port: str = Field(env_var='ZEBEE_PORT')

class SecureConfig(InsecureConfig):
    root_certificates: str = Field(env_var='SSL_ROOT_CA')
    private_key: str = Field(env_var='SSL_PRIVATE_KEY')
    certificate_chain: Optional[str] = Field(env_var='SSL_CERTIFICATE_CHAIN')

@logger.catch(message='Failed to load config variables', reraise=True)
def generate_config_from_env()->ConnectionConfig:
    cls_map = {
        'SECURE': SecureConfig,
        'INSECURE': InsecureConfig,
        'CAMUNDA_CLOUD': CloudConfig
    }

    connection_type = os.environ.get('CAMUNDA_CONNECTION_TYPE', None)
    if connection_type is None:
        raise ValueError('CAMUNDA_CONNECTION_TYPE is not defined')
    
    config_cls = cls_map.get(connection_type, None)

    if config_cls is None:
        raise ValueError(
            f'Unknown CAMUNDA_CONNECTION_TYPE ({connection_type})'
        )

    data = {}
    for field_name, field in config_cls.__fields__.items():
        env_var = field.field_info.extra['env_var']
        data[field_name] = os.environ.get(env_var, None)

    return config_cls(**data)