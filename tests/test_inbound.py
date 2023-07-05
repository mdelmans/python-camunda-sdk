import random

from unittest import TestCase

from python_camunda_sdk import InboundConnector

from util import async_test

class ValidInbound(InboundConnector):
    counter: int  = 0

    async def run(self):
        if self.counter == 0:
            self.counter = 1
            return None
        else:
            return {'random_number': random.randint(1, 100)}

    class ConnectorConfig:
        name = "random_inbound"
        cycle_duration = 1


class TestInboundConnector(TestCase):
    @async_test
    async def test_valid(self):
        connector = ValidInbound(correlation_key="foo")
        ret = await connector.loop()
        self.assertIsInstance(ret, dict)
        self.assertIn('random_number', ret)

    def test_no_run(self):
        with self.assertRaises(AttributeError):
            class NoRunInbound(InboundConnector):
                class ConnectorConfig:
                    name = "random_inbound"
                    cycle_duration = 10
