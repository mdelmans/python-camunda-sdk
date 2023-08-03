from typing import Optional, Union, get_args
from types import NoneType

from abc import abstractmethod

import inspect

from loguru import logger

from pydantic import BaseModel
from pydantic.main import ModelMetaclass

from pyzeebe import Job

from python_camunda_sdk.types import SimpleTypes
from python_camunda_sdk.connectors.config import ConnectorConfig


class ConnectorMetaclass(ModelMetaclass):
    """Connector metaclass.

    Validates that connector definitions are correct.
    """

    @logger.catch(
        reraise=True,
        message='Invalid connector definition'
    )
    def __new__(
        mcs,
        cls_name,
        bases,
        namespace,
        base_config_cls=ConnectorConfig,
        **kwargs
    ):
        cls = super().__new__(
            mcs,
            cls_name,
            bases,
            namespace,
            **kwargs
        )

        cls._base_config_cls = base_config_cls

        if bases != (BaseModel,) and bases != (Connector,):
            cls._generate_config()
            cls._check_run_method()
            cls._check_return_annotation()
            cls._extra_pre_init_checks()

        return cls

    def _generate_config(cls) -> None:
        """Converts ConnectorConfig class inside the connector class into a
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
        if (
            run_method is None
            or hasattr(run_method, '__isabstractmethod__')
        ):
            raise AttributeError(
                'Connector must have a run(self, config) method defined.'
                f' {cls} appears to have no run() method'
            )

    def _check_return_annotation(cls) -> None:
        signature = inspect.signature(cls.run)
        return_annotation = signature.return_annotation

        if return_annotation == signature.empty:
            raise AttributeError(
                'Connector that return nothing must be annotated with'
                '-> None.'
                f' {cls} return nothing.'
            )

        if (
            return_annotation != NoneType
            and not issubclass(return_annotation, BaseModel)
            and return_annotation not in get_args(SimpleTypes)
        ):
            raise AttributeError(
                f'Connector returns invalid type ({return_annotation})'
            )
        cls._return_type = return_annotation

    def _extra_pre_init_checks(cls) -> None:
        pass


class Connector(BaseModel, metaclass=ConnectorMetaclass):
    """Connector base class.

    !!! warning
        Should not be used directly. Use
        [OutboundConnector]
        [python_camunda_sdk.connectors.outbound.OutboundConnector] or
        [InboundConnector]
        [python_camunda_sdk.connectors.outbound.OutboundConnector]
        instead.
    """
    @logger.catch(
        reraise=True,
        message='Failed to execute connector method'
    )
    async def _execute(
        self,
        job: Job
    ) -> Optional[Union[BaseModel, SimpleTypes]]:
        """Execute connector `run` method while passing the connector config.

        Arguments:
            job: An instance of a job.

        Raises:
            ValueError: If type of the returned value does not match the
                type-hint.
        """
        if inspect.iscoroutinefunction(self.run):
            ret_value = await self.run(self._config)
        else:
            ret_value = self.run(self._config)

        if not isinstance(ret_value, self._return_type):
            raise ValueError(
                'Mismatch between return annotation and returned value in'
                f' {self.__class__}. Expected {self._return_type}, got'
                f' {type(ret_value)}'
            )

        return_variable_name = job.custom_headers.get(
                'resultVariable', None
            )

        if return_variable_name is not None:
            return_value = None

            if isinstance(ret_value, BaseModel):
                return_value = ret_value.dict()
            else:
                return_value = ret_value

            return {return_variable_name: return_value}

    @abstractmethod
    async def run(self, config: ConnectorConfig) -> None:
        """The main connector method that must be overridden by
        subclasses.

        Arguments:
            config: Configuration of the connector.
        """
        raise NotImplementedError
