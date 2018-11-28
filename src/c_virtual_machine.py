import operator
from numbers import Number
from typing import List

from c_instruction import Instruction, OpCode


class VirtualMachine:
    def __init__(self):
        self._code: List[Instruction]
        self._labels = {}
        self._symbols = {}
        self._pc = 0
        self._last_line_empty = True

    def run(self, code: List[Instruction]):
        self._code = code
        self._read_labels()
        while self._pc < len(code):
            method = VirtualMachine.HANDLERS[code[self._pc].opcode]
            method(self, *code[self._pc].args)
            self._pc += 1
        if not self._last_line_empty:
            print()

    def _plus(self, oper1, oper2, dest):
        self._operation(oper1, oper2, dest, operator.add)

    def _minus(self, oper1, oper2, dest):
        self._operation(oper1, oper2, dest, operator.sub)

    def _mult(self, oper1, oper2, dest):
        self._operation(oper1, oper2, dest, operator.mul)

    def _div(self, oper1, oper2, dest):
        self._operation(oper1, oper2, dest, operator.truediv)

    def _mod(self, oper1, oper2, dest):
        self._operation(oper1, oper2, dest, operator.mod)

    def _equal(self, oper1, oper2, dest):
        self._operation(oper1, oper2, dest, operator.eq, logic=True)

    def _not_equal(self, oper1, oper2, dest):
        self._operation(oper1, oper2, dest, operator.ne, logic=True)

    def _greater_than(self, oper1, oper2, dest):
        self._operation(oper1, oper2, dest, operator.gt, logic=True)

    def _greater_equal(self, oper1, oper2, dest):
        self._operation(oper1, oper2, dest, operator.ge, logic=True)

    def _less_then(self, oper1, oper2, dest):
        self._operation(oper1, oper2, dest, operator.lt, logic=True)

    def _less_equal(self, oper1, oper2, dest):
        self._operation(oper1, oper2, dest, operator.le, logic=True)

    def _and(self, oper1, oper2, dest):
        self._operation(oper1, oper2, dest, operator.and_, logic=True)

    def _or(self, oper1, oper2, dest):
        self._operation(oper1, oper2, dest, operator.or_, logic=True)

    def _not(self, oper, dest):
        val = self._get_variables(oper)
        self._symbols[dest] = int(not val)

    def _label(self, _):
        pass

    def _if(self, condition, label_if, label_else):
        cond_val = self._get_variables(condition)
        if cond_val:
            self._pc = self._labels[label_if]
        else:
            self._pc = self._labels[label_else]

    def _jump(self, label):
        self._pc = self._labels[label]

    def _call(self, command, arg1, arg2=None):
        string = self._format(arg1)
        print(string, end='')
        if command == 'print':
            self._last_line_empty = string.endswith('\n')
        elif command == 'scan_int':
            string = input()
            try:
                value = int(string)
            except ValueError:
                value = int(float(string))
            self._symbols[arg2] = value
        elif command == 'scan_float':
            self._symbols[arg2] = float(input())

    def _format(self, value: str):
        if not isinstance(value, str):
            return str(value)
        if value.startswith('"'):
            return value[1:-1].replace('\\n', '\n')
        return str(self._symbols[value])

    def _read_labels(self):
        for i, instruction in enumerate(self._code):
            if instruction.opcode == OpCode.LABEL:
                self._labels[instruction.args[0]] = i

    def _operation(self, oper1, oper2, dest, operator_, logic=False):
        val1, val2 = self._get_variables(oper1, oper2)
        result = operator_(val1, val2)
        if logic:
            self._symbols[dest] = int(result)
        else:
            self._symbols[dest] = result

    def _get_variables(self, *args):
        values = [None for _ in range(len(args))]
        for i, value in enumerate(args):
            if isinstance(value, Number):
                values[i] = value
            else:
                values[i] = self._symbols[value]
        return values if len(values) > 1 else values[0]

    HANDLERS = {
        OpCode.PLUS: _plus,
        OpCode.MINUS: _minus,
        OpCode.MULT: _mult,
        OpCode.DIV: _div,
        OpCode.MOD: _mod,
        OpCode.EQ: _equal,
        OpCode.NEQ: _not_equal,
        OpCode.GT: _greater_than,
        OpCode.GEQ: _greater_equal,
        OpCode.LT: _less_then,
        OpCode.LEQ: _less_equal,
        OpCode.AND: _and,
        OpCode.OR: _or,
        OpCode.NOT: _not,
        OpCode.LABEL: _label,
        OpCode.IF: _if,
        OpCode.JUMP: _jump,
        OpCode.CALL: _call
    }
