# Create process

This steps will help you to create a simple process and use the connectors loaded to your runtime.

1. Make sure the runtime is active and has both `LogConnector` and `SleepConnector` are loaded.

	```console
	$ python example/runtime.py
	2023-08-03 21:09:30.829 | INFO     | python_camunda_sdk.runtime.runtime:main:114 - Loading LogConnector (log)
	2023-08-03 21:09:30.829 | INFO     | python_camunda_sdk.runtime.runtime:main:114 - Loading Sleep (sleep)
	2023-08-03 21:09:30.829 | INFO     | python_camunda_sdk.runtime.runtime:main:117 - Starting runtime
	```

2. Import templates to Modeller.

	!!! tip "Cloud Modeller"

		Open Modeler, and upload the template using New -> Upload files menu.

	!!! tip "Desktop Modeller"
		Save the template into `resources/element-templates/` directory. See [Configuring templates](https://docs.camunda.io/docs/components/modeler/desktop-modeler/element-templates/configuring-templates/) in the official Caunda documentation for details.

3. Create a simple process.

	![Process](/img/process.png)

	=== "Say hi!"
		`Type`: Service Task

		`Template`: LogConnector

		`Message to log`: Hello Camunda!

	=== "Sleep"
		`Type`: Service Task

		`Template`: SleepConnector

		`Duration of sleep in seconds`: 2

		`Correlation key`: "demo_key"

		`Message name`: "Wake up"

	=== "Wake up"
		`Type`: Message Intermediate Catch Event

		`Message name`: Wake up

		`Subscription correlation key`: "demo_key"

	=== "Say bye!"

		`Type`: Service Task

		`Template`: LogConnector

		`Message to log`: Goodbye!

4. Start the process instance. You should see logs apper in the console
	
	```console
	2023-08-03 21:55:01.306 | INFO     | log:run:15 - LogConnector: Hello Camunda!
	2023-08-03 21:55:03.340 | INFO     | log:run:15 - LogConnector: Goodbye!
	```

<style>
	.md-footer__link--next{
		display: none;
	}
</style>