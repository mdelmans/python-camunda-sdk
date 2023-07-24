# Generate outbound template

You can generate templates for use in Camunda SaaS or Camunda Modeler from you outbound connectors.

Python Camunda SDK includes a `generate_template` command-line tool to help you.

``` console
$ generate_template --help

Usage: generate_template [OPTIONS] CONNECTOR FILENAME

	Generates a template from a CONNECTOR and saves it to FILENAME.

	CONNECTOR must be a a full class name including the module name, e.g.
	mymodule.submodule.MyConnector.

Options:
	--help  Show this message and exit.
```

For example, if `LogConnector`, we use in this guide is part of the `example` module, we can run

``` console
$ generate_template example.LogConnector log.json
Generated template for example.LogConnector
```

## Template conversion

`LogConnector` class have been converted to a template:

* `name` of the template was picked up from `ConnectorConfig.name`
* `zeebe:taskDefinition:type` was set to `ConnectorConfig.type` (not visible in Modeler).
* `message` field of the `LogConnector` was converted into a `zeebe:input` property.
* A `zeebe:taskHeader` with key 'resultVariable' was added to allow users define the name of the variable where the output of the `LogConnector.run` method will be stored.

=== "Template rendering"

	![Image title](/img/template.png){ align=left, width="300" }

=== "Template json"

	``` json linenums="1" title="example/log.json"
	--8<-- "log.json"
	```

=== "LogConnector"

	```py linenums="1" title="example/log.py"
	--8<-- "log.py"
	```


## Importing template to Camunda SaaS

Open Modeler, and upload the template using New -> Upload files menu.

## Importing template to Camunda Modeler

Save the template into `resources/element-templates/` directory. See [Configuring templates](https://docs.camunda.io/docs/components/modeler/desktop-modeler/element-templates/configuring-templates/) in the official Caunda documentation for details.