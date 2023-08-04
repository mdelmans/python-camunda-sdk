from typing import List, Optional

import inspect

from uuid import uuid4

from pydantic import BaseModel, Field

from python_camunda_sdk.connectors import Connector, InboundConnector


class Binding(BaseModel):
    type: str
    name: Optional[str]
    source: Optional[str]
    key: Optional[str]


class CamundaProperty(BaseModel):
    binding: Binding
    label: Optional[str]
    type: Optional[str]
    value: Optional[str]
    group: Optional[str]
    feel: Optional[str]


class Group(BaseModel):
    id: Optional[str]
    label: Optional[str]


class CamundaTemplate(BaseModel):
    """Camunda template object that follows (incompletely) the official
    template schema.

    Attributes:
        template_schema: Alias to `$schema`
        name:
        model_id:
        applies_to:
        properties:
        groups:
    """

    template_schema: str = Field(
        default=(
            "https://unpkg.com/@camunda/zeebe-element-templates-json-schema"
            "@0.9.0/resources/schema.json"
        ),
        alias="$schema",
    )

    name: str
    model_id: Optional[str] = Field(
        alias="id", default_factory=lambda: str(uuid4())
    )
    applies_to: Optional[List[str]] = Field(
        alias="appliesTo", default=["bpmn:ServiceTask"]
    )
    properties: Optional[List[CamundaProperty]]
    groups: List[Group]


def generate_input_props(cls: Connector) -> List[CamundaProperty]:
    props = []
    for field_name, field in cls.__fields__.items():
        if not field_name.startswith("_"):
            prop = CamundaProperty(
                label=field.field_info.description or field_name,
                binding=Binding(type="zeebe:input", name=field_name),
                group="input",
                feel="optional",
                type="String",
            )
            props.append(prop)

    return props


def generate_inbound_config_props(cls: InboundConnector):
    correlation_key_prop = CamundaProperty(
        label="Correlation key",
        binding=Binding(type="zeebe:input", name="correlation_key"),
        group="config",
        feel="optional",
        type="String",
    )

    message_name_prop = CamundaProperty(
        label="Message name",
        binding=Binding(type="zeebe:input", name="message_name"),
        group="config",
        feel="optional",
        type="String",
    )

    return [correlation_key_prop, message_name_prop]


def generate_output_prop(cls: Connector) -> Optional[CamundaProperty]:
    signature = inspect.signature(cls.run)

    return_annotation = signature.return_annotation

    if return_annotation != signature.empty:
        prop = CamundaProperty(
            label="Result variable",
            binding=Binding(type="zeebe:taskHeader", key="resultVariable"),
            type="String",
            group="output",
        )
        return prop


def generate_template(cls: Connector) -> CamundaTemplate:
    """Generate Camunda template from the connector class definition.

    Converts connector class into a Camunda template mapping class fields
    into template inputs.

    Agrs:
        cls: Connector class.

    Example:
        ```py
        class MyConnector(OutboundConnector):
            name: str = Field(description="Name")

            class ConnectorConfig:
                name = "MyConnector"
                type = "my_connector"
                timeout = 1
        ```
        Will be converted to a template called `MyConnector`. The `name`
        field will be converted to an input `name` and label
        `Name`. Attributes of the `ConnectorConfig` class will be mapped to
        the attributes of the template.

    Returns:
        A camunda template object that can be converted to json for import
            into Camunda SAAS or desktop modeller.
    """
    props = generate_input_props(cls)

    signature = inspect.signature(cls.run)

    return_annotation = signature.return_annotation

    if return_annotation != signature.empty:
        prop = CamundaProperty(
            label="Result variable",
            binding=Binding(type="zeebe:taskHeader", key="resultVariable"),
            type="String",
            group="output",
        )
        props.append(prop)

    task_type_prop = CamundaProperty(
        value=cls.config.type,
        type="Hidden",
        binding=Binding(type="zeebe:taskDefinition:type"),
    )

    props.append(task_type_prop)

    groups = [
        Group(id="input", label="Input"),
        Group(id="output", label="Output"),
    ]

    if issubclass(cls, InboundConnector):
        props.extend(generate_inbound_config_props(cls))
        groups.append(Group(id="config", label="Configuration"))

    template = CamundaTemplate(
        name=cls.config.name, properties=props, groups=groups
    )

    return template
