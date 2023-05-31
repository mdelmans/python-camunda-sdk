from typing import Union
from pyzeebe.errors import BusinessError

SimpleTypes = Union[int, float, str, bool, list, dict]

__all__ = ['BusinessError', 'SimpleTypes']
