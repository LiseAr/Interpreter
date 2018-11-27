from typing import List, Optional, Tuple, Union

from c_token import TokenType
from c_instruction import Instruction

Value = Union[int, float, str]


class Result:
    """Class to be returned from each grammar rule to the rule that called it.
    """
    def __init__(self, *,
                 lvalue: Optional[bool] = None,
                 type_: Optional[TokenType] = None):
        self.lvalue = lvalue
        self.type_ = type_
        self.value: List[Value] = []
        self.code: List[Tuple[List[Instruction], Optional[Value]]] = []

    def __add__(self, other: 'Result'):
        if not isinstance(other, Result):
            raise TypeError()
        lvalue = self.lvalue and other.lvalue
        type_ = self.type_ if self.type_ is not None else other.type_
        value = self.value.copy()
        value.extend(other.value)
        code = self.code.copy()
        code.extend(other.code)
        result = Result(lvalue=lvalue, type_=type_)
        result.value = value
        result.code = code
        return result

    def __radd__(self, other):
        if not other:
            return self
        return self.__add__(other)
