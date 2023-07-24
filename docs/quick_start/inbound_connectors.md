# Define an inbound connector

!!! warning
	Inbound connectors are experimental. 

Implementation of inbound connectors is different from the original one.

Instead of automatically fetching Intermediate Catch
Events from the Operate server, this runtime relies on a process
instance activating the inbound connector explicitly using an service task.

Once activated, the runtime will create a new async task that will execute the connector logic and publish a message to Zeebe with the result.

Similar to outbound connectors, inbound connectors are defined as classes derived from `InboundConnector`.

```py linenums="1" title="example/sleep.py"
--8<-- "sleep.py"
```

Once started, this connector will sleep for a given duration and then publish a message to Zebee with a name and correlation key configured in Modeler.

