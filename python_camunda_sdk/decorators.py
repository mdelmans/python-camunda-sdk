from typing import Optional
from pydantic import validate_arguments
from python_camunda_sdk import OutboundConnector, InboundConnector


@validate_arguments
def outbound_connector(
    name: str,
    type: str,
    timeout: Optional[int] = 10
):
    def wrapper(cls):
        class ConnectorConfig:
            name = name
            type = type
            timeout = timeout

        new_cls = type(
            cls.__name__,
            (OutboundConnector, cls),
            {'ConnectorConfig': ConnectorConfig}
        )
        return new_cls
    return wrapper


@validate_arguments
def inbound_connector(
    name: str,
    cycle: Optional[int] = 1
):
    def wrapper(cls):
        class ConnectorConfig:
            name = name
            cycle = cycle

        new_cls = type(
            cls.__name__,
            (InboundConnector, cls),
            {'ConnectorConfig': ConnectorConfig}
        )
        return new_cls
    return wrapper
