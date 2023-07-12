from typing import List, Optional

import inspect

from uuid import uuid4

from pydantic import BaseModel, Field

from python_camunda_sdk.outbound import OutboundConnector

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
    tempate_schema: str = Field(
        default=(
            "https://unpkg.com/@camunda/zeebe-element-templates-json-schema"
            "@0.9.0/resources/schema.json"
        ),
        alias="$schema"
    )

    name: str
    model_id: Optional[str] = Field(
        alias='id',
        default_factory=lambda: str(uuid4())
    )
    applies_to: Optional[List[str]] = Field(
        alias="appliesTo",
        default=["bpmn:ServiceTask"]
    )
    properties: Optional[List[CamundaProperty]]
    groups: List[Group]

def generate_template(cls: OutboundConnector):
    """Generate Camunda template from the connector class definition.

    Converts connector class into a Camunda template mapping class fields
    into template inputs.
    
    Agrs:
        cls: Connector class.

    Example:
        class MyConnector(OutboundConnector):
            name: str = Field(description="Name")

            class ConnectorConfig:
                name = "MyConnector"
                type = "my_connector"
                timeout = 1

        Will be converted to a template with input called 'name' and label
        'Name'. Attributes of the `ConnectorConfig` class will be mapped to
        the attributes of the template.

    Returns:
        A camunda template object that can be converted to json for import
        into Camunda SAAS or desktop modeller.
    """
    props = []
    for field_name, field in cls.__fields__.items():
        if not field_name.startswith('_'):
            prop = CamundaProperty(
                label=field.field_info.description,
                binding=Binding(
                    type="zeebe:input",
                    name=field_name
                ),
                group='input',
                feel='optional',
                type='String'
            )
            props.append(prop)

    signature = inspect.signature(cls.run)

    return_annotation = signature.return_annotation

    if return_annotation != signature.empty:
        prop = CamundaProperty(
            label="Result variable",
            binding=Binding(
                type="zeebe:taskHeader",
                key="resultVariable"
            ),
            type="String",
            group="output"
        )
        props.append(prop)
        # for field_name, field in return_annotation.__fields__.items():
        #     if not field_name.startswith('_'):
        #         prop = CamundaProperty(
        #             label=field.field_info.description,
        #             binding=Binding(
        #                 type="zeebe:output",
        #                 source=f"={field_name}"
        #             )
        #         )
        #         props.append(prop)

    task_type_prop = CamundaProperty(
        value=cls._config.type,
        type="Hidden",
        binding=Binding(
            type="zeebe:taskDefinition:type"
        )
    )

    props.append(task_type_prop)

    template = CamundaTemplate(
        name=cls._config.name,
        properties=props,
        groups=[
            Group(
                id='input',
                label='Input'
            ),
            Group(
                id='output',
                label='Output'
            )
        ]
    )

    return template
