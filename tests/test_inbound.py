import asyncio

from pydantic import ValidationError

from unittest import TestCase

from python_camunda_sdk import InboundConnector

from util import async_test, DummyJob, DummyClient


class ValidInbound(InboundConnector):
    counter: int = 0

    async def run(self, config) -> int:
        return self.counter + 1

    class ConnectorConfig:
        name = "Valid inbound"
        type = "valid_inbound"


class TestInboundConnector(TestCase):
    @async_test
    async def test_valid(self):
        job = DummyJob(result_variable="ret")
        client = DummyClient()

        connector = ValidInbound(counter=1)
        ret = await connector._execute(
            job=job,
            client=client,
            message_name="test_message",
            correlation_key="key_x",
        )
        self.assertIsNone(ret)
        self.assertEqual(client.message_name, "test_message")
        self.assertEqual(client.correlation_key, "key_x")
        self.assertEqual(client.variables, {"ret": 2})

    @async_test
    async def test_to_task_conversion(self):
        client = DummyClient()
        job = DummyJob(result_variable="ret")

        task = ValidInbound.to_task(client=client)

        ret = await task(
            job=job,
            message_name="test_message",
            correlation_key="key_x",
            counter=1,
        )

        await asyncio.sleep(1)

        self.assertIsNone(ret)
        self.assertEqual(client.message_name, "test_message")
        self.assertEqual(client.correlation_key, "key_x")
        self.assertEqual(client.variables, {"ret": 2})

    @async_test
    async def test_task_validation_failure(self):
        task = ValidInbound.to_task(client=None)
        job = DummyJob(result_variable="ret")
        with self.assertRaises(ValidationError):
            await task(
                job=job,
                message_name="test_message",
                correlation_key="key_x",
                counter="foo",
            )
