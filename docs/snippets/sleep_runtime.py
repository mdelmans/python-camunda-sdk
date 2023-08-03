from python_camunda_sdk import CamundaRuntime, InsecureConfig

from log import LogConnector
from sleep import SleepConnector


config = InsecureConfig(
    hostname="127.0.0.1"
)

runtime = CamundaRuntime(
    config=config,
    outbound_connectors=[LogConnector],
    inbound_connectors=[SleepConnector]
)

if __name__ == "__main__":
    runtime.start()
