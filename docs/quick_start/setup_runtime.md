# Setup a runtime


## Overview
Runtime connects to Zeebe instance and listens to service tasks handled by the connectors.

Runtime does not discover connectors automatically. You need to let runtime know which connectors you want it to handle by passing connector classes through `outbound_connectors` argument.

=== "runtime.py"

	``` py linenums="1"
	--8<-- "runtime.py"
	```

=== "log.py"
	``` py
	--8<-- "log.py"
	```

## Configuration

In addition to `outbiund_connectors` you need to give runtime credentials to Zeebe instance.

### With config object

You can pass configuration object with the details of Zeebe instance you want to connect. The examples of supported configs are below.

=== "Insecure config"

	``` py
	from python_camunda_sdk import InsecureConfig

	config = InsecureConfig(
		host='127.0.0.1',
		port=26500
	)
	```

=== "Secure config"

	``` py
	from python_camunda_sdk import SecureConfig

	config = SecureConfig(
		host='127.0.0.1',
		port=26500,
		root_certificates='''
		-----BEGIN CERTIFICATE-----
		xxx
		-----BEGIN CERTIFICATE-----
		'''
		private_key='''
		-----BEGIN RSA PRIVATE KEY-----
		xxx
		-----BEGIN RSA PRIVATE KEY-----
		'''
		certificate_chain=''
	)
	```

=== "Cloud config"

	``` py
	from python_camunda_sdk import CloudConfig

	config = CloudConfig(
		client_id='jYsgv.SryJYQlcpobk-tZZP~2R60xpNY',
		client_secret='55kddTbk~yZBFb2NH5GtebWHkSoK1z.TG7G1Hn-n.mH_f4ihpZAUop1-sryxHnyV',
		cluster_id='7bc802fc-7bf4-4800-b84a-596628d1ed08'
	)
	```

### With environmental variables

You can also use environment variables to configure connection to Zeebe.

=== "All connection types"

	| Variable 					| Description         		                 |
	|---------------------------|--------------------------------------------|
	| `CAMUNDA_CONNECTION_TYPE`	| Connection type                            |
	
	| Connection type value     | Description         		                 |
	|---------------------------|--------------------------------------------|
	| INSECURE                  | Insecure connection to a self-hosted Zeebe |
	| SECURE                    | Secure connection to a self-hosted Zeebe   |
	| CAMUNDA_CLOUD             | Conneection to Camunda Cloud               |

=== "Insecure"

	| Variable 					| Description         		                 |
	|---------------------------|--------------------------------------------|
	| `ZEBEE_HOSTNAME`        	| Hostname or IP address of Zeebe            |
	| `ZEBEE_PORT`       	    | The port Zeebe is listening on             |

=== "Secure"

	| Variable 					| Description         		                 |
	|---------------------------|--------------------------------------------|
	| `ZEBEE_HOSTNAME`        	| Hostname or IP address of Zeebe            |
	| `ZEBEE_PORT`        	    | The port Zeebe is listening on             |
	| `SSL_ROOT_CA`             | SSL certificate                            |
	| `SSL_PRIVATE_KEY`         | SSL private key                            |
	| `SSL_CERTIFICATE_CHAIN`   | SSL certificate chain                      |

=== "Cloud"

	| Variable 					| Description         		                 |
	|---------------------------|--------------------------------------------|
	| `CAMUNDA_CLIENT_ID`       | Client id                                  |
	| `CAMUNDA_CLIENT_SECRET`   | Client seecret                             |
	| `CAMUNDA_CLUSTER_ID`      | Camunda cluster id                         |


