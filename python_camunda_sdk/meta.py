from loguru import logger

from pydantic import BaseModel
from pydantic.main import ModelMetaclass


class ConnectorMetaclass(ModelMetaclass):
    """Base class for connector metaclass"""

    _base_config_cls = None

    def __new__(mcs, cls_name, bases, namespace, **kwargs):
        cls = super().__new__(
            mcs,
            cls_name,
            bases,
            namespace,
            **kwargs
        )

        if bases != (BaseModel,):
            cls.generate_config()

        return cls

    @logger.catch(reraise=True)
    def generate_config(cls) -> None:
        """Generate config.

        Converts ConnectorConfig class inside the connector class into a
        `_config` attribute of type defined in `_base_config_cls`.

        Raises:
            AttributeError: if class does not have `ConnectorConfig` subclass
                defined.
        """
        config_cls = getattr(
            cls,
            'ConnectorConfig',
            None
        )
        data = {}

        if config_cls is None:
            raise AttributeError(
                f'{cls} is missing ConnectorConfig'
            )

        for field_name, field in cls._base_config_cls.__fields__.items():

            if not hasattr(config_cls, field_name):
                continue

            attr = getattr(config_cls, field_name)

            data[field_name] = attr

        cls._config = cls._base_config_cls(**data)
