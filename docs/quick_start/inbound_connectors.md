# Define an inbound connector

Implementation of inbound connectors is different from the official Camunda SDK.

Instead of automatically fetching Intermediate Catch
Events from the Operate server, this runtime relies on a process
instance activating the inbound connector explicitly using a service task.

Once activated, the runtime will create a new async task that will execute the connector logic and publish a message to Zeebe with the result.

Similar to outbound connectors, inbound connectors are defined as classes derived from `InboundConnector`.

=== "example/sleep.py"

	```py linenums="1"
	--8<-- "sleep.py"
	```

=== "example/__init__.py"

	``` py linenums="1"
	--8<-- "sleep_init.py"
	```

Once started, this connector will sleep for a given duration and then publish a message to Zebee with a name and correlation key configured in Modeler.

Import the `SleepConnector` and add it to the runtime `inbound_connectors`.

=== "example/runtime.py"

	```py
	--8<-- "sleep_runtime.py"
	```

=== "example/sleep.py"

	```py linenums="1"
	--8<-- "sleep.py"
	```

=== "example/__init__.py"

	``` py linenums="1"
	--8<-- "sleep_init.py"
	```

Restart the runtime.

```console
$ python example/runtime.py
2023-08-03 21:09:30.829 | INFO     | python_camunda_sdk.runtime.runtime:main:114 - Loading LogConnector (log)
2023-08-03 21:09:30.829 | INFO     | python_camunda_sdk.runtime.runtime:main:114 - Loading Sleep (sleep)
2023-08-03 21:09:30.829 | INFO     | python_camunda_sdk.runtime.runtime:main:117 - Starting runtime
```

Now both `LogConnector` and `SleepConnector` are active.