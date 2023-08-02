"""
These configuration classes define how to connect to a Zeebe instance.

Keys given in description must be used if you prefer to set up
connection using environmental variables.

In addition, you must set `CAMUNDA_CONNECTION_TYPE` to either
`SECURE`, `INSECURE` or `CAMUNDA_CLOUD`.

Example Cloud config:
    ``` py
    from python_camunda_sdk import CloudConfig

    config = CloudConfig(
        client_id='jYsgv.SryJYQlcpobk-tZZP~2R60xpNY',
        client_secret='55kddTbk~yZBFb2NH5GtebWHkSoK1z.TG7G1Hn-n.mH_f4ihpZAUop1-sryxHnyV',
        cluster_id='7bc802fc-7bf4-4800-b84a-596628d1ed08'
    )
    ```

Example Insecure config:
    ``` py
    from python_camunda_sdk import InsecureConfig

    config = InsecureConfig(
        host='127.0.0.1',
        port=26500
    )
    ```

Example secure config:
    ```py
    config = SecureConfig(
        host='127.0.0.1',
        port=26500,
        root_certificates='''
        -----BEGIN CERTIFICATE-----
        xxx
        -----BEGIN CERTIFICATE-----
        '''
        private_key='''
        -----BEGIN RSA PRIVATE KEY-----
        xxx
        -----BEGIN RSA PRIVATE KEY-----
        '''
        certificate_chain=''
    )
    ```
"""
import os
from typing import Optional

from pydantic import BaseModel, Field

from loguru import logger


class ConnectionConfig(BaseModel):
    """Base class for connection configuration.
    """
    pass


class CloudConfig(ConnectionConfig):
    """Configuration for connection to Camunda SaaS.

    Attributes:
        client_id: `CAMUNDA_CLIENT_ID`
        client_secret: `CAMUNDA_CLIENT_SECRET`
        cluster_id: `CAMUNDA_CLUSTER_ID`
    """
    client_id: str = Field(env_var='CAMUNDA_CLIENT_ID')
    client_secret: str = Field(env_var='CAMUNDA_CLIENT_SECRET')
    cluster_id: str = Field(env_var='CAMUNDA_CLUSTER_ID')


class InsecureConfig(ConnectionConfig):
    """Configuration for connecting insecurely to self-hosted Zeebe
    instance.

    Attributes:
        hostname: `ZEBEE_HOSTNAME`
        port: `ZEBEE_PORT`
    """
    hostname: str = Field(env_var='ZEBEE_HOSTNAME')
    port: str = Field(env_var='ZEBEE_PORT')


class SecureConfig(InsecureConfig):
    """Configuration for connecting securely to self-hosted Zeebe
    instance.

    !!! warning
        In addition should have hostname and port set.

    Attributes:
        root_certificates: `SSL_ROOT_CA`
        private_key: `SSL_PRIVATE_KEY`
        certificate_chain: `SSL_CERTIFICATE_CHAIN`
    """
    root_certificates: str = Field(env_var='SSL_ROOT_CA')
    private_key: str = Field(env_var='SSL_PRIVATE_KEY')
    certificate_chain: Optional[str] = Field(env_var='SSL_CERTIFICATE_CHAIN')


@logger.catch(message='Failed to load config variables', reraise=True)
def generate_config_from_env() -> ConnectionConfig:
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
