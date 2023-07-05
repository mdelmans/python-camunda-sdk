from unittest import TestCase

from pydantic import ValidationError, BaseModel

from python_camunda_sdk import OutboundConnector

from util import (
    true_body,
    none_body,
    dict_body,
    async_test
)

class DummyModel(BaseModel):
    foo: int


def model_body(self, config):
    return DummyModel(foo=1)


class TestOutbound(TestCase):

    def generate_outbound_connector(self, run_body, ret_type):
        class DummyOutboundConnector(OutboundConnector):
            def run(self, config) -> ret_type:
                return run_body(self, config)

            class ConnectorConfig:
                name = "dummy"
                type = "dummy"
                timeout = 10
                output_variable_name = "output"

        return DummyOutboundConnector

    def test_new_simple(self):
        cls = self.generate_outbound_connector(true_body, bool)

        self.assertIsNotNone(cls)

    def test_new_no_config(self):
        with self.assertRaises(AttributeError):
            class DummyOutboundConnector(OutboundConnector):
                def run(self, config):
                    return None

    def test_new_bad_config(self):
        with self.assertRaises(ValidationError):
            class DummyOutboundConnector(OutboundConnector):
                def run(self, config):
                    return None

                class ConnectorConfig:
                    name = "dummy"
                    type = "dummy"
                    timeout = "twenty"

    @async_test
    async def test_async_run(self):
        class DummyOutboundConnector(OutboundConnector):
            async def run(self, config) -> bool:
                return True

            class ConnectorConfig:
                name = "dummy"
                type = "dummy"
                timeout = 10
                output_variable_name = "output"

        connector = DummyOutboundConnector()

        ret = await connector.execute()
        self.assertTrue(ret)

    @async_test
    async def test_sync_run(self):
        cls = self.generate_outbound_connector(true_body, bool)

        connector = cls()

        ret = await connector.execute()
        self.assertTrue(ret)

    @async_test
    async def test_return_none(self):
        cls = self.generate_outbound_connector(none_body, None.__class__)

        connector = cls()

        self.assertIsNotNone(connector)

        ret = await connector.execute()

        self.assertIsNone(ret)

    @async_test
    async def test_return_dict(self):
        cls = self.generate_outbound_connector(dict_body, dict)

        connector = cls()

        self.assertIsNotNone(connector)

        ret = await connector.execute()

        self.assertIsInstance(ret, dict)

    @async_test
    async def test_return_model(self):
        cls = self.generate_outbound_connector(model_body, DummyModel)

        connector = cls()

        self.assertIsNotNone(connector)

        ret = await connector.execute()

        self.assertIsInstance(ret, DummyModel)

    @async_test
    async def test_return_wrong_type(self):
        cls = self.generate_outbound_connector(model_body, int)

        connector = cls()

        self.assertIsNotNone(connector)
        with self.assertRaises(ValueError):
            await connector.execute()

    def test_no_run_method(self):
        with self.assertRaises(AttributeError):
            class DummyOutboundConnector(OutboundConnector):
                class ConnectorConfig:
                    name = "dummy"
                    type = "dummy"
                    timeout = 10
                    output_variable_name = "output"

    def test_no_return_annotation(self):
        with self.assertRaises(AttributeError):
            class DummyOutboundConnector(OutboundConnector):
                def run(self, config):
                    return True

                class ConnectorConfig:
                    name = "dummy"
                    type = "dummy"
                    timeout = 10
                    output_variable_name = "output"

    def test_no_output_variable_name(self):
        with self.assertRaises(AttributeError):
            class DummyOutboundConnector(OutboundConnector):
                def run(self, config) -> bool:
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
                def run(self, config) -> DummyClass:
                    return True

                class ConnectorConfig:
                    name = "dummy"
                    type = "dummy"
                    timeout = 10

    @async_test
    async def test_to_task_conversion(self):
        cls = self.generate_outbound_connector(true_body, bool)

        task = cls.to_task()

        ret = await task()

        self.assertTrue(ret)

    @async_test
    async def test_task_validation_failure(self):
        class DummyOutboundConnector(OutboundConnector):
            input_field: int

            def run(self, config) -> int:
                return 1

            class ConnectorConfig:
                name = "dummy"
                type = "dummy"
                timeout = 10
                output_variable_name = "output"

        task = DummyOutboundConnector.to_task()
        with self.assertRaises(ValidationError):
            await task(input_field='foo')

    @async_test
    async def test_task_model_conversion(self):
        class DummyOutboundConnector(OutboundConnector):
            input_field: int

            def run(self, config) -> DummyModel:
                return DummyModel(foo=self.input_field + 1)

            class ConnectorConfig:
                name = "dummy"
                type = "dummy"
                timeout = 10
                output_variable_name = "output"

        task = DummyOutboundConnector.to_task()

        ret = await task(input_field=1)

        self.assertIsInstance(ret, dict)
        self.assertIn('foo', ret)
        self.assertEquals(ret['foo'], 2)
