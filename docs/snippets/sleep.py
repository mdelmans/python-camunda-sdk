import asyncio

from pydantic import Field

from python_camunda_sdk import InboundConnector


class SleepConnector(InboundConnector):
    duration: int = Field(description="Duration of sleep in seconds")

    async def run(self) -> bool:
        await asyncio.sleep(self.duration)
        return True

    class ConnectorConfig:
        name = "Sleep"
        type = 'sleep'
