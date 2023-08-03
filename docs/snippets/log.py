from pydantic import BaseModel, Field
from loguru import logger

from python_camunda_sdk import OutboundConnector


class StatusModel(BaseModel):
    status: str


class LogConnector(OutboundConnector):
    message: str = Field(description="Message to log")

    async def run(self, config) -> StatusModel:
        logger.info(f"LogConnector: {self.message}")

        return StatusModel(status="ok")

    class ConnectorConfig:
        name = "LogConnector"
        type = "log"
