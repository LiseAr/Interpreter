from enum import Enum, unique
from typing import Union

Operand = Union[int, float, str]


@unique
class OpCode(Enum):
    """OpCodes for the virtual machine."""
    PLUS = '+'
    MINUS = '-'
    MULT = '*'
    DIV = '/'
    IDIV = '//'
    MOD = '%'
    EQ = '=='
    NEQ = '!='
    GT = '>'
    GEQ = '>='
    LT = '<'
    LEQ = '<='
    AND = '&&'
    OR = '||'
    NOT = '!'
    LABEL = 'label'
    IF = 'if'
    JUMP = 'jump'
    CALL = 'call'


class Instruction:
    """Virtual machine instruction."""
    def __init__(self):
        self.opcode: OpCode
        self.args: tuple

    @staticmethod
    def factory(*args) -> 'Instruction':
        instruction = Instruction()
        instruction.opcode = args[0]
        instruction.args = tuple(args[1:])
        return instruction

    @staticmethod
    def operation(operator: str, op1: Operand, op2: Operand,
                  result: str) -> 'Instruction':
        return Instruction.factory(OpCode(operator), op1, op2, result)

    @staticmethod
    def unary(operator: str, operand, result: str) -> 'Instruction':
        return Instruction.factory(OpCode(operator), operand, result)

    @staticmethod
    def label(name: str) -> 'Instruction':
        return Instruction.factory(OpCode.LABEL, name)

    @staticmethod
    def if_(expr: str, true_label: str, false_label: str) -> 'Instruction':
        return Instruction.factory(OpCode.IF, expr, true_label, false_label)

    @staticmethod
    def jump(label: str) -> 'Instruction':
        return Instruction.factory(OpCode.JUMP, label)

    @staticmethod
    def call(name: str, *args) -> 'Instruction':
        return Instruction.factory(OpCode.CALL, name, *args)

    def change_arg(self, index: int, value):
        self.args = tuple(a if i != index else value
                          for i, a in enumerate(self.args))

    def __str__(self):
        return f'({self.opcode.value}, {", ".join(str(a) for a in self.args)})'

    def __repr__(self):
        return f'Instruction{self.__str__()}'
