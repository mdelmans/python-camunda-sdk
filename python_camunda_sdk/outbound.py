import inspect

from typing import Union, Callable, Optional

from loguru import logger

from pydantic import BaseModel
from pydantic import ValidationError

from python_camunda_sdk.config import OutboundConnectorConfig
from python_camunda_sdk.meta import ConnectorMetaclass
from python_camunda_sdk.types import SimpleTypes
from python_camunda_sdk import CamundaProperty, Binding, CamundaTemplate


class OutboundConnectorMetaclass(ConnectorMetaclass):
    _base_config_cls = OutboundConnectorConfig


class OutboundConnector(BaseModel, metaclass=OutboundConnectorMetaclass):
    """Outbound connector base class"""

    async def execute(self):
        """Execute connector `run` method while passing the connector config.
        """
        return await self.run(self._config)

    async def run(
        self,
        config: OutboundConnectorConfig
    ) -> Optional[Union[BaseModel, SimpleTypes]]:
        """Virtual method that contains the connector logic.

        Args:
            config: a config object defined for the connector class.

        Returns:
            Optional outcome of the connector logic.

        Raises:
            NotImlementedError: if `run` method is not overridden.
        """
        raise NotImplementedError

    @classmethod
    def generate_template(cls) -> CamundaTemplate:
        """Generate Camunda template from the connector class definition.

        Converts connector class into a Camunda template mapping class fields
        into template inputs.

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
                    )
                )
                props.append(prop)

        signature = inspect.signature(cls.execute)

        return_annotation = signature.return_annotation

        if return_annotation != signature.empty:

            for field_name, field in return_annotation.__fields__.items():
                if not field_name.startswith('_'):
                    prop = CamundaProperty(
                        label=field.field_info.description,
                        binding=Binding(
                            type="zeebe:output",
                            source=f"={field_name}"
                        )
                    )
                    props.append(prop)

        task_type_prop = CamundaProperty(
            value=cls._type,
            type="Hidden",
            binding=Binding(
                type="zeebe:taskDefinition:type"
            )
        )

        props.append(task_type_prop)

        template = CamundaTemplate(
            name=cls._name,
            properties=props
        )

        return template

    @classmethod
    def to_task(cls) -> Callable[..., Union[BaseModel, SimpleTypes]]:
        """Converts connector class into a Python function.

        Returns:
            A Python function that validates arguments and executes the
            connector logic.
        """
        async def task(**kwargs) -> Union[BaseModel, SimpleTypes]:
            try:
                connector = cls(**kwargs)
            except ValidationError as e:
                logger.exception(
                    'Failed to validate arguments for'
                    f'{cls._name}'
                )
                raise e

            ret = await connector.execute()
            if isinstance(ret, BaseModel):
                return ret.dict()
            else:
                return ret
        return task
