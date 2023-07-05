from typing import Optional
from pydantic import BaseModel


class OutboundConnectorConfig(BaseModel):
    name: str
    type: str
    timeout: Optional[int] = 10
    output_variable_name: Optional[str]


class InboundConnectorConfig(BaseModel):
    name: str
    cycle_duration: Optional[int] = 1
