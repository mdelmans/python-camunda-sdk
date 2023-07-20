# Deffine an inbound connector

!!! warning
	Inbound connectors are experimental and have not been properly tested. 

Inbond connectors are experimental and implementation is different from the original.

Instead of automatically fetching Intermediate Catch
Events from the Operate server, this runtime relies on a process
instance activating the inbound connector explicitly using an in-built
`_activate_inbound_connector` service task.

Once activated, the runtime will create a new async task that will execute the connector logic and publish a mesaage to Zeebe with the result.

Similar to outbound connectors, inbound connectors are defined as classes derrived from `InboundConnector`.

```py
```