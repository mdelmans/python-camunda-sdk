import asyncio

class DummyJob:
    def __init__(self, result_variable: str = None):
        self.custom_headers = {'resultVariable': result_variable}

class DummyClient:
    async def publish_message(self, name, correlation_key, variables):
        self.message_name = name
        self.correlation_key = correlation_key
        self.variables = variables

def true_body(self, config):
    return True


def none_body(self, config):
    return None


def dict_body(self, config):
    return {'foo': '1'}


def async_test(coro):
    def wrapper(*args, **kwargs):
        loop = asyncio.new_event_loop()
        try:
            return loop.run_until_complete(coro(*args, **kwargs))
        finally:
            loop.close()
    return wrapper