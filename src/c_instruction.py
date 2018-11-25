from enum import auto, Enum
from typing import Union


Operand = Union[int, float, str]


class OpCode(Enum):
    """OpCodes for the virtual machine."""
    PLUS = auto()
    MINUS = auto()
    MULT = auto()
    DIV = auto()
    MOD = auto()
    EQ = auto()
    NEQ = auto()
    GT = auto()
    GEQ = auto()
    LT = auto()
    LEQ = auto()
    AND = auto()
    OR = auto()
    NOT = auto()
    LABEL = auto()
    IF = auto()
    JUMP = auto()
    CALL = auto()


OPERATION = {
    '+': OpCode.PLUS,
    '-': OpCode.MINUS,
    '*': OpCode.MULT,
    '/': OpCode.DIV,
    '%': OpCode.MOD,
    '==': OpCode.EQ,
    '!=': OpCode.NEQ,
    '>': OpCode.GT,
    '>=': OpCode.GEQ,
    '<': OpCode.LT,
    '<=': OpCode.LEQ,
    '&&': OpCode.AND,
    '||': OpCode.OR,
    '!': OpCode.NOT
}


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
        return Instruction.factory(OPERATION[operator], op1, op2, result)

    @staticmethod
    def unary(operator: str, operand, result: str) -> 'Instruction':
        return Instruction.factory(OPERATION[operator], operand, result)

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
    def call(name: str) -> 'Instruction':
        return Instruction.factory(OpCode.CALL, name)
