from typing import List, Optional
from pydantic import BaseModel, Field
from uuid import uuid4


class Binding(BaseModel):
    type: str
    name: Optional[str]
    source: Optional[str]


class CamundaProperty(BaseModel):
    binding: Binding
    label: Optional[str]
    type: Optional[str]
    value: Optional[str]


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
