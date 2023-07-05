import os
from unittest import TestCase

from python_camunda_sdk import CamundaRuntime


class TestRuntime(TestCase):
	def test_init(self):
		runtime = CamundaRuntime()
		self.assertIsNotNone(runtime)
