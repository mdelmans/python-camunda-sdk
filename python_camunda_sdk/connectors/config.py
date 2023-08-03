from typing import Optional

from pydantic import BaseModel


class ConnectorConfig(BaseModel):
    """Base configuration class for connectors.

    Attributes:
        name: Name of the connector. This will be displayed as a name
            of the template.
        type: Type of the connector. This will correspond to the type of
            the service task that will be calling the connector.
        timeout: Timeout for the connector.
    """
    name: str
    type: str
    timeout: Optional[int] = 10


class OutboundConnectorConfig(ConnectorConfig):
    """Outbound connector configuration.
    """
    pass


class InboundConnectorConfig(ConnectorConfig):
    """Inbound connector configuration.
    """
    pass
