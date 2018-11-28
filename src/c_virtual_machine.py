import operator
from numbers import Number
from typing import List

from c_instruction import Instruction, OpCode


def to_number(string):
    try:
        return int(string)
    except ValueError:
        try:
            return float(string)
        except ValueError:
            return string


class VirtualMachine:
    HANDLERS: dict

    def __init__(self):
        self._code: List[Instruction]
        self._labels = dict
        self._symbols = dict
        self._pc = 0
        self._last_line_empty = True

    def run(self, code: List[Instruction], *args):
        self._code = code
        self._symbols = {f'__arg__{i}': to_number(v)
                         for i, v in enumerate(args)}
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

    def _idiv(self, oper1, oper2, dest):
        self._operation(oper1, oper2, dest,
                        lambda x, y: int(operator.floordiv(x, y)))

    def _mod(self, oper1, oper2, dest):
        self._operation(oper1, oper2, dest, operator.mod, to_int=True)

    def _eq(self, oper1, oper2, dest):
        self._operation(oper1, oper2, dest, operator.eq, to_int=True)

    def _neq(self, oper1, oper2, dest):
        self._operation(oper1, oper2, dest, operator.ne, to_int=True)

    def _gt(self, oper1, oper2, dest):
        self._operation(oper1, oper2, dest, operator.gt, to_int=True)

    def _geq(self, oper1, oper2, dest):
        self._operation(oper1, oper2, dest, operator.ge, to_int=True)

    def _lt(self, oper1, oper2, dest):
        self._operation(oper1, oper2, dest, operator.lt, to_int=True)

    def _leq(self, oper1, oper2, dest):
        self._operation(oper1, oper2, dest, operator.le, to_int=True)

    def _and(self, oper1, oper2, dest):
        self._operation(oper1, oper2, dest, operator.and_, to_int=True)

    def _or(self, oper1, oper2, dest):
        self._operation(oper1, oper2, dest, operator.or_, to_int=True)

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
        else:
            string = input()
            self._last_line_empty = True
            if command == 'scan_int':
                try:
                    value = int(string)
                except ValueError:
                    value = int(float(string))
            elif command == 'scan_float':
                value = float(string)
            self._symbols[arg2] = value

    def _format(self, value: str):
        if not isinstance(value, str):
            return str(value)
        if value.startswith('"'):
            return value[1:-1].replace('\\n', '\n')
        return str(self._symbols[value])

    def _read_labels(self):
        self._labels = {}
        for i, instruction in enumerate(self._code):
            if instruction.opcode == OpCode.LABEL:
                self._labels[instruction.args[0]] = i

    def _operation(self, oper1, oper2, dest, operator_, to_int=False):
        val1, val2 = self._get_variables(oper1, oper2)
        result = operator_(val1, val2)
        if to_int:
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


VirtualMachine.HANDLERS = {oc: getattr(VirtualMachine, f'_{oc.name.lower()}')
                           for oc in OpCode}
