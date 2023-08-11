import os
from typing import Optional

from pydantic import BaseModel, Field

from loguru import logger


class ConnectionConfig(BaseModel):
    """Base class for connection configuration."""

    pass


class CloudConfig(ConnectionConfig):
    """Configuration for connection to Camunda SaaS.

    Attributes:
        client_id: `CAMUNDA_CLIENT_ID`
        client_secret: `CAMUNDA_CLIENT_SECRET`
        cluster_id: `CAMUNDA_CLUSTER_ID`
        region: `CAMUNDA_REGION`
    """

    client_id: str = Field(
        json_schema_extra={
            "env_var": "CAMUNDA_CLIENT_ID"
        }
    )
    client_secret: str = Field(
        json_schema_extra={
            "env_var": "CAMUNDA_CLIENT_SECRET"
        }
    )
    cluster_id: str = Field(
        json_schema_extra={
            "env_var": "CAMUNDA_CLUSTER_ID"
        }
    )
    region: str = Field(
        json_schema_extra={
            "env_var": "CAMUNDA_REGION"
        }
    )


class InsecureConfig(ConnectionConfig):
    """Configuration for connecting insecurely to self-hosted Zeebe
    instance.

    Attributes:
        hostname: `ZEBEE_HOSTNAME`
        port: `ZEBEE_PORT`
    """

    hostname: str = Field(
        json_schema_extra={
            "env_var": "ZEBEE_HOSTNAME"
        }
    )
    port: Optional[int] = Field(
        default=26500,
        json_schema_extra={
            "env_var": "ZEBEE_PORT"
        }
    )


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

    root_certificates: str = Field(
        json_schema_extra={
            "env_var": "SSL_ROOT_CA"
        }
    )
    private_key: str = Field(
        json_schema_extra={
            "env_var": "SSL_PRIVATE_KEY"
        }
    )
    certificate_chain: Optional[str] = Field(
        default=None,
        json_schema_extra={
            "env_var": "SSL_CERTIFICATE_CHAIN"
        }
    )


@logger.catch(message="Failed to load config variables", reraise=True)
def generate_config_from_env() -> ConnectionConfig:
    cls_map = {
        "SECURE": SecureConfig,
        "INSECURE": InsecureConfig,
        "CAMUNDA_CLOUD": CloudConfig,
    }

    connection_type = os.environ.get("CAMUNDA_CONNECTION_TYPE", None)
    if connection_type is None:
        raise ValueError("CAMUNDA_CONNECTION_TYPE is not defined")

    config_cls = cls_map.get(connection_type, None)

    if config_cls is None:
        raise ValueError(
            f"Unknown CAMUNDA_CONNECTION_TYPE ({connection_type})"
        )

    data = {}
    for field_name, field in config_cls.model_fields.items():
        env_var = field.json_schema_extra["env_var"]
        data[field_name] = os.environ.get(env_var, None)

    return config_cls(**data)
