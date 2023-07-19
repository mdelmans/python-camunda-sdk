from python_camunda_sdk import CamundaRuntime, InsecureConfig

from log import LogConnector

config = InsecureConfig(
    host="127.0.0.1"
)

runtime = CamundaRuntime(
    config=config,
    outbound_connectors=[LogConnector]
)

if __name__ == "__main__":
    runtime.start()
