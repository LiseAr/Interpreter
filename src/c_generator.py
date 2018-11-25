from enum import Enum, auto
from c_token import TokenType


class func_type(Enum):
    IF = auto()
    WHILE = auto()
    PRINT = auto()
    SCAN = auto()


class CodeGenerator:

    TYPE = {
        'if': func_type.IF,
        'while': func_type.WHILE,
        'print': func_type.PRINT,
        'scan': func_type.SCAN
        }

    def __init__(self):

        self.functions = {
            '_stmt': self._stmt,
            '_io_stmt': self._io_stmt,
            '_else_part': self._else_part,
            '_expr': self._expr,
            '_uno': self._uno,
            '_fator': self._fator,
            '_consome': self._consome,
            '_resto_atrib': self._resto_atrib
        }

        self.code_list = list()
        self.consome_stack = list()
        self.label_stack = list()
        self.result_stack = list()
        self.func_stack = list()
        self.generate_label = self.generate_label()
        self.generate_tmp = self.generate_tmp()
        self.type = None

    def generate(self, name='', result=None):
        if name not in self.functions:
            return
        self.func_stack.append(name)
        self.functions[name](result) if result else self.functions[name]()


    @property
    def infinity(self):
        return 99999999

    def generate_label(self):
        for i in range(self.infinity):
            yield f'label-{i}'

    def generate_tmp(self):
        for i in range(self.infinity):
            yield f'tmp-{i}'

    @property
    def last_token(self):
        return self.consome_stack[-1] if self.consome_stack else None

    def _function(self):
        self.code_list.append(('$', None, None, None))

    def _arg_list(self):
        pass

    def _arg(self):
        pass

    def _resto_arg_list(self):
        pass

    def _type(self):
        pass

    def _bloco(self):
        pass

    def _stmt_list(self):
        pass

    def _stmt(self):
        if self.type == func_type.IF:
            if self.label_stack:
                _else = self.label_stack.pop()
                self.code_list.append(('label', _else, None, None))
        if self.type == func_type.WHILE:
            inicio = self.label_stack.pop()
            fim = self.label_stack.pop()
            self.code_list.extend([('jump', inicio, None, None),
                                   ('label', fim, None, None)])
            self.type = None

    def _declaration(self):
        pass

    def _ident_list(self):
        pass

    def _resto_ident_list(self):
        pass

    def _for_stmt(self):
        pass

    def _opt_expr(self):
        pass

    def _io_stmt(self):
        if self.type == func_type.SCAN:
            self.code_list.append(('call', 'scan', None, None))
        elif self.type == func_type.PRINT:
            self.code_list.append(('call', 'print', None, None))

    def _out_list(self):
        pass

    def _out(self):
        pass

    def _resto_out_list(self):
        pass

    def _while_stmt(self):
        pass

    def _if_stmt(self):
        pass

    def _else_part(self):
        if self.type == func_type.IF:
            if self.label_stack:
                fim = self.label_stack.pop()
                self.code_list.append(('label', fim, None, None))
                self.type = None

    def _expr(self):
        if self.type == func_type.IF:
            self.label_stack.append(next(self.generate_label))  # label: fim
            _else = next(self.generate_label)
            self.code_list.append(('if', self.result, None, _else))
            self.label_stack.append(_else)
        elif self.type == func_type.WHILE:
            fim = next(self.generate_label)
            inicio = next(self.generate_label)
            _tuple = self.code_list.pop()
            self.code_list.extend([('label', inicio, None, None), _tuple])
            self.code_list.append(('if', self.code_list[-1][4], None, fim))
            self.label_stack.append(fim)
            self.label_stack.append(inicio)

    def _atrib(self):
        # expr
        
        # fator (nda)
        pass

    def _resto_atrib(self):
        pass

    def _or(self):
        pass

    def _resto_or(self):
        pass

    def _and(self):
        pass

    def _resto_and(self):
        pass

    def _not(self):
        pass

    def _rel(self):
        pass

    def _resto_rel(self):
        pass

    def _add(self):
        pass

    def _resto_add(self):
        pass

    def _mult(self):
        pass

    def _resto_mult(self):
        if len(self.func_stack) >= 3:
            if self.func_stack.pop().pop().pop() == '_resto_mult':
                self.code_list.append(self.last_token.name, )
        pass

    def _uno(self):
        if self.last_token and \
           self.last_token.id == TokenType.SUB:
            self.consome_stack.pop()
            self.code_list.append(('-', '0', next(self.generate_tmp),
                                   self.result))

    def _fator(self):
        if self.consome_stack and \
           self.consome_stack[-1].id in {TokenType.IDENT, TokenType.NUMINT,
                                         TokenType.NUMFLOAT}:
            self.result = self.consome_stack.pop().name

    def _consome(self, token):
        self.consome_stack.append(token)
        if not self.type and token.name in self.TYPE:
            self.type = self.TYPE[token.name]
