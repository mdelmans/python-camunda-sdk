from unittest import TestCase

from pydantic import ValidationError, BaseModel

from python_camunda_sdk import OutboundConnector

from util import true_body, none_body, dict_body, async_test, DummyJob


class DummyModel(BaseModel):
    foo: int


def model_body(self):
    return DummyModel(foo=1)


class TestOutbound(TestCase):
    def generate_outbound_connector(self, run_body, ret_type):
        class DummyOutboundConnector(OutboundConnector):
            def run(self) -> ret_type:
                return run_body(self)

            class ConnectorConfig:
                name = "dummy"
                type = "dummy"
                timeout = 10

        return DummyOutboundConnector

    def test_new_simple(self):
        cls = self.generate_outbound_connector(true_body, bool)

        self.assertIsNotNone(cls)

    def test_new_no_config(self):
        with self.assertRaises(AttributeError):

            class DummyOutboundConnector(OutboundConnector):
                def run(self):
                    return None

    def test_new_bad_config(self):
        with self.assertRaises(ValidationError):

            class DummyOutboundConnector(OutboundConnector):
                def run(self):
                    return None

                class ConnectorConfig:
                    name = "dummy"
                    type = "dummy"
                    timeout = "twenty"

    @async_test
    async def test_async_run(self):
        class DummyOutboundConnector(OutboundConnector):
            async def run(self) -> bool:
                return True

            class ConnectorConfig:
                name = "dummy"
                type = "dummy"
                timeout = 10

        connector = DummyOutboundConnector()

        job = DummyJob(result_variable="ret")
        ret = await connector._execute(job=job)

        self.assertIsInstance(ret, dict)
        self.assertIn("ret", ret)
        self.assertTrue(ret["ret"])

    @async_test
    async def test_sync_run(self):
        cls = self.generate_outbound_connector(true_body, bool)

        connector = cls()

        job = DummyJob(result_variable="ret")
        ret = await connector._execute(job=job)

        self.assertIsInstance(ret, dict)
        self.assertIn("ret", ret)
        self.assertTrue(ret["ret"])

    @async_test
    async def test_return_none(self):
        cls = self.generate_outbound_connector(none_body, None.__class__)

        connector = cls()

        self.assertIsNotNone(connector)

        job = DummyJob(result_variable="ret")
        ret = await connector._execute(job=job)

        self.assertIsInstance(ret, dict)
        self.assertIn("ret", ret)
        self.assertIsNone(ret["ret"])

    @async_test
    async def test_return_dict(self):
        cls = self.generate_outbound_connector(dict_body, dict)

        connector = cls()

        self.assertIsNotNone(connector)

        job = DummyJob(result_variable="ret")
        ret = await connector._execute(job=job)

        self.assertIsInstance(ret, dict)
        self.assertIn("ret", ret)
        self.assertIsInstance(ret["ret"], dict)

    @async_test
    async def test_return_model(self):
        cls = self.generate_outbound_connector(model_body, DummyModel)

        connector = cls()

        self.assertIsNotNone(connector)

        job = DummyJob(result_variable="ret")
        ret = await connector._execute(job=job)

        self.assertIsInstance(ret, dict)
        self.assertIn("ret", ret)
        self.assertIsInstance(ret["ret"], dict)

    @async_test
    async def test_return_wrong_type(self):
        cls = self.generate_outbound_connector(model_body, int)

        connector = cls()

        self.assertIsNotNone(connector)
        with self.assertRaises(ValueError):
            job = DummyJob(result_variable="ret")
            await connector._execute(job=job)

    def test_no_run_method(self):
        with self.assertRaises(AttributeError):

            class DummyOutboundConnector(OutboundConnector):
                class ConnectorConfig:
                    name = "dummy"
                    type = "dummy"
                    timeout = 10

    def test_no_return_annotation(self):
        with self.assertRaises(AttributeError):

            class DummyOutboundConnector(OutboundConnector):
                def run(self):
                    return True

                class ConnectorConfig:
                    name = "dummy"
                    type = "dummy"
                    timeout = 10

    def test_unsupported_return_type(self):
        class DummyClass:
            pass

        with self.assertRaises(AttributeError):

            class DummyOutboundConnector(OutboundConnector):
                def run(self) -> DummyClass:
                    return True

                class ConnectorConfig:
                    name = "dummy"
                    type = "dummy"
                    timeout = 10

    @async_test
    async def test_to_task_conversion(self):
        cls = self.generate_outbound_connector(true_body, bool)

        job = DummyJob(result_variable="ret")

        task = cls.to_task(client=None)

        ret = await task(job=job)

        self.assertIsInstance(ret, dict)
        self.assertIn("ret", ret)
        self.assertTrue(ret["ret"])

    @async_test
    async def test_task_validation_failure(self):
        class DummyOutboundConnector(OutboundConnector):
            input_field: int

            def run(self) -> int:
                return 1

            class ConnectorConfig:
                name = "dummy"
                type = "dummy"
                timeout = 10

        task = DummyOutboundConnector.to_task(client=None)
        job = DummyJob(result_variable="ret")
        with self.assertRaises(ValidationError):
            await task(job=job, input_field="foo")
