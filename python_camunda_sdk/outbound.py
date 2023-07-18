import inspect

from typing import Union, Dict, Optional, get_args
from collections.abc import Coroutine

from loguru import logger

from pydantic import BaseModel
from pydantic import ValidationError

from pyzeebe import Job

from python_camunda_sdk.config import OutboundConnectorConfig
from python_camunda_sdk.meta import ConnectorMetaclass
from python_camunda_sdk.types import SimpleTypes


class OutboundConnectorMetaclass(ConnectorMetaclass):
    _base_config_cls = OutboundConnectorConfig

    def _extra_pre_init_checks(cls) -> None:
        cls._check_return_annotation()

    def _check_return_annotation(cls) -> None:
        signature = inspect.signature(cls.run)
        return_annotation = signature.return_annotation

        if return_annotation == signature.empty:
            raise AttributeError(
                'Connector that return nothing must be annotated with'
                '-> None.'
                f' {cls} return nothing.'
            )
        # if return_annotation in get_args(SimpleTypes):
        #     if cls._config.output_variable_name is None:
        #         raise AttributeError(
        #             'Connector returning a non-dict value must have'
        #             'output_variable_name set in config.'
        #             f' {cls} returns {return_annotation}'
        #         )
        # elif (
        #         return_annotation not in (dict, Dict, None.__class__)
        #         and not issubclass(return_annotation, BaseModel)
        # ):
        #     raise AttributeError(
        #         'Return type of a connector run() method must be'
        #         ' either a simpel type, dict or a BaseModel.'
        #         f' {cls} returns {return_annotation}'
        #     )
        cls._return_type = return_annotation



class OutboundConnector(BaseModel, metaclass=OutboundConnectorMetaclass):
    """Outbound connector base class"""

    @logger.catch(
        reraise=True,
        message="Failed to execute connector method"
    )
    async def execute(self) -> Optional[Union[BaseModel, SimpleTypes]]:
        """Execute connector `run` method while passing the connector config.
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

        return ret_value

    @classmethod
    def to_task(cls) -> Coroutine[..., Optional[Union[BaseModel, SimpleTypes]]]:
        """Converts connector class into a Python function.

        Returns:
            A Python function that validates arguments and executes the
            connector logic.
        """
        async def task(job: Job, **kwargs) -> Union[BaseModel, SimpleTypes]:
            try:
                connector = cls(**kwargs)
            except ValidationError as e:
                logger.exception(
                    'Failed to validate arguments for '
                    f'{cls._config.name}'
                )
                raise e

            ret = await connector.execute()

            return_variable_name = job.custom_headers.get(
                'resultVariable', None
            )

            if return_variable_name is not None:
                return_value = None
                
                if isinstance(ret, BaseModel):
                    return_value = ret.dict()
                else:
                    return_value = ret

                return {return_variable_name: return_value}

        return task
