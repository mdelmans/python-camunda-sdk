import os
from unittest import TestCase

from python_camunda_sdk import (
	CamundaRuntime,
	CloudConfig,
	SecureConfig,
	InsecureConfig
)


class TestRuntime(TestCase):
	def test_cloud_config(self):
		config = CloudConfig(
			client_id='client_id',
    		client_secret='client_secret',
    		cluster_id='cluster_id' 
		) 
		runtime = CamundaRuntime(config=config)
		self.assertIsNotNone(runtime)

	def test_secure_config(self):
		config = SecureConfig(
			hostname='hostname',
			port=0,
			root_certificates='root_certificates',
    		private_key='private_key',
    		certificate_chain='certificate_chain'
		) 
		runtime = CamundaRuntime(config=config)
		self.assertIsNotNone(runtime)

	def test_insecure_config(self):
		config = InsecureConfig(
			hostname='hostname',
			port=0
		) 
		runtime = CamundaRuntime(config=config)
		self.assertIsNotNone(runtime)

	def test_cloud_config_from_env(self):
		os.environ['CAMUNDA_CONNECTION_TYPE'] = 'CAMUNDA_CLOUD'
		os.environ['CAMUNDA_CLIENT_ID'] = 'client_id'
		os.environ['CAMUNDA_CLIENT_SECRET'] = 'client_sectret'
		os.environ['CAMUNDA_CLUSTER_ID'] = 'cluster_id'
		
		runtime = CamundaRuntime()
		self.assertIsNotNone(runtime)

		config = runtime._config

		self.assertIsInstance(config, CloudConfig)

	def test_secure_config_from_env(self):
		os.environ['CAMUNDA_CONNECTION_TYPE'] = 'SECURE'
		os.environ['ZEBEE_HOSTNAME']= 'hostname'
		os.environ['ZEBEE_PORT']='0'
		os.environ['SSL_ROOT_CA']='root_certificates'
		os.environ['SSL_PRIVATE_KEY']='private_key'
		os.environ['SSL_CERTIFICATE_CHAIN']='certificate_chain'
		
		runtime = CamundaRuntime()
		self.assertIsNotNone(runtime)

		config = runtime._config

		self.assertIsInstance(config, SecureConfig)

	def test_insecure_config_from_env(self):
		os.environ['CAMUNDA_CONNECTION_TYPE'] = 'INSECURE'
		os.environ['ZEBEE_HOSTNAME']= 'hostname'
		os.environ['ZEBEE_PORT']='0'

		runtime = CamundaRuntime()
		self.assertIsNotNone(runtime)

		config = runtime._config

		self.assertIsInstance(config, InsecureConfig)

	def test_unknown_config_from_env(self):
		os.environ['CAMUNDA_CONNECTION_TYPE'] = 'INVALID'
		with self.assertRaises(ValueError):
			CamundaRuntime()

	def test_undefined_config_from_env(self):
		del os.environ['CAMUNDA_CONNECTION_TYPE']
		with self.assertRaises(ValueError):
			CamundaRuntime()