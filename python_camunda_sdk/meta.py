from loguru import logger

from pydantic import BaseModel
from pydantic.main import ModelMetaclass


class ConnectorMetaclass(ModelMetaclass):
    """Base class for connector metaclass"""

    _base_config_cls = None

    @logger.catch(
        reraise=True,
        message="Invalid connector definion"
    )
    def __new__(mcs, cls_name, bases, namespace, **kwargs):
        cls = super().__new__(
            mcs,
            cls_name,
            bases,
            namespace,
            **kwargs
        )

        if bases != (BaseModel,):
            cls._generate_config()
            cls._check_run_method()
            cls._extra_pre_init_checks()

        return cls

    def _generate_config(cls) -> None:
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

    def _check_run_method(cls) -> None:
        run_method = getattr(cls, 'run', None)
        if run_method is None:
            raise AttributeError(
                'Connector must have a run(self, config) method defined.'
                f' {cls} appers to have no run() method'
            )

    def _extra_pre_init_checks(cls) -> None:
        pass
