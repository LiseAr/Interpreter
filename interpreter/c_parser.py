import sys
from collections.abc import Collection
from enum import auto, Flag
from functools import partial, wraps
from typing import Callable

from c_code_generator import CodeGenerator
from c_grammar import FIRST, FOLLOW
from c_lexer import Lexer
from c_parser_result import Result
from c_parser_tree import ParserTree
from c_symbol_table import SymbolTable
from c_token import Token, TokenType as T
from c_virtual_machine import VirtualMachine


class ParserError(Exception):
    """Exception class for parser errors."""
    pass


def rule_head(method):
    var_name = method.__name__.lstrip('_')

    @wraps(method)
    def new_method(self) -> Result:
        self.tree.push(var_name)
        result = method(self)
        self.tree.pop()
        return result

    new_method.first = FIRST[var_name]
    new_method.follow = FOLLOW[var_name]
    return new_method


def rule(function=None, *, new_scope=False, lvalue=None):
    if function is None:
        return partial(rule, new_scope=new_scope, lvalue=lvalue)

    method_name = f'{function.__name__.rstrip("_")}'
    pre_method_name = f'{method_name}_pre'

    def new_function(parser: 'Parser') -> Result:
        if new_scope:
            parser.symbol_table.enter_block()

        pre_method = code_method = None
        if ParserFeatures.CODE_GENERATION in parser.features:
            code_method = getattr(
                parser.code_generator, method_name,
                getattr(parser.code_generator, f'{method_name}_', None))
            pre_method = getattr(parser.code_generator, pre_method_name, None)

        if pre_method is not None:
            pre_method()
        result = function(parser)
        if code_method is not None:
            result = code_method(result)

        if new_scope:
            parser.symbol_table.leave_block()

        if lvalue is not None:
            result.lvalue = lvalue
        return result

    return new_function


class ParserFeatures(Flag):
    NONE = 0
    TREE_DOT_GENERATION = auto()
    CODE_GENERATION = auto()
    SAVE_CODE_TO_FILE = auto()
    EXECUTE_CODE = auto()
    DEFAULT = (TREE_DOT_GENERATION | CODE_GENERATION |
               SAVE_CODE_TO_FILE | EXECUTE_CODE)


class Parser:
    def __init__(self, lexer: Lexer, features=ParserFeatures.DEFAULT):
        self.curr_token: Token
        self.code_generator = CodeGenerator()
        self.features = features
        self.lexer = lexer
        self.symbol_table = SymbolTable()
        self.tree = ParserTree()
        self.virtual_machine = VirtualMachine()

    def parse(self):
        self.curr_token = self.lexer.get_token()
        result = self._function()
        if ParserFeatures.TREE_DOT_GENERATION in self.features:
            with open('tree.dot', 'w') as file:
                file.write(str(self.tree))
        if ParserFeatures.CODE_GENERATION in self.features:
            if ParserFeatures.SAVE_CODE_TO_FILE in self.features:
                with open('code.out', 'w') as file:
                    file.write('\n'.join(str(c) for c in result.code[0][0]))
            if ParserFeatures.EXECUTE_CODE in self.features:
                self.virtual_machine.run(result.code[0][0], *sys.argv[2:])

    @rule_head
    def _function(self):
        @rule(new_scope=True)
        def function(_parser):
            return self._produce(self._type, T.IDENT, T.OPAR, self._arg_list,
                                 T.CPAR, self._bloco, T.EOF)
        return function(self)

    @rule_head
    def _arg_list(self):
        @rule
        def arg_list(_parser):
            result = self._produce(self._arg, self._resto_arg_list)
            self._declare_variables(result)
            return result

        @rule
        def arg_list_empty(_parser):
            return Result()

        if self.curr_token.type_ in Parser._arg_list.first:
            return arg_list(self)
        return arg_list_empty(self)

    @rule_head
    def _arg(self):
        @rule
        def arg(_parser):
            return self._produce(self._type, T.IDENT)
        return arg(self)

    @rule_head
    def _resto_arg_list(self):
        @rule
        def resto_arg_list(_parser):
            return self._produce(T.COMMA, self._arg_list)

        @rule
        def resto_arg_list_empty(_parser):
            return Result()

        if self.curr_token.type_ in Parser._resto_arg_list.first:
            return resto_arg_list(self)
        return resto_arg_list_empty(self)

    @rule_head
    def _type(self):
        @rule
        def type_(_parser):
            return self._produce({T.INT, T.FLOAT})
        return type_(self)

    @rule_head
    def _bloco(self):
        @rule(new_scope=True)
        def bloco(_parser):
            return self._produce(T.OBRKT, self._stmt_list, T.CBRKT)
        return bloco(self)

    @rule_head
    def _stmt_list(self):
        @rule
        def stmt_list_stmt(_parser):
            return self._produce(self._stmt, self._stmt_list)

        @rule
        def stmt_list_declaration(_parser):
            return self._produce(self._declaration, self._stmt_list)

        @rule
        def stmt_list_empty(_parser):
            return Result()

        if self.curr_token.type_ in Parser._stmt.first:
            return stmt_list_stmt(self)
        if self.curr_token.type_ in Parser._declaration.first:
            return stmt_list_declaration(self)
        return stmt_list_empty(self)

    @rule_head
    def _stmt(self):
        @rule
        def stmt_for(_parser):
            return self._produce(self._for_stmt)

        @rule
        def stmt_io(_parser):
            return self._produce(self._io_stmt)

        @rule
        def stmt_while(_parser):
            return self._produce(self._while_stmt)

        @rule
        def stmt_if(_parser):
            return self._produce(self._if_stmt)

        @rule
        def stmt_bloco(_parser):
            return self._produce(self._bloco)

        @rule
        def stmt_expr(_parser):
            return self._produce(self._expr, T.SEMICOLON)

        @rule
        def stmt_break(_parser):
            return self._produce(T.BREAK, T.SEMICOLON)

        @rule
        def stmt_continue(_parser):
            return self._produce(T.CONTINUE, T.SEMICOLON)

        @rule
        def stmt_return(_parser):
            return self._produce(T.RETURN, self._fator, T.SEMICOLON)

        @rule
        def stmt_null(_parser):
            return self._produce(T.SEMICOLON)

        if self.curr_token.type_ in Parser._for_stmt.first:
            return stmt_for(self)
        if self.curr_token.type_ in Parser._io_stmt.first:
            return stmt_io(self)
        if self.curr_token.type_ in Parser._while_stmt.first:
            return stmt_while(self)
        if self.curr_token.type_ in Parser._if_stmt.first:
            return stmt_if(self)
        if self.curr_token.type_ in Parser._bloco.first:
            return stmt_bloco(self)
        if self.curr_token.type_ in Parser._expr.first:
            return stmt_expr(self)
        if self.curr_token.type_ == T.BREAK:
            return stmt_break(self)
        if self.curr_token.type_ == T.CONTINUE:
            return stmt_continue(self)
        if self.curr_token.type_ == T.RETURN:
            return stmt_return(self)
        return stmt_null(self)

    @rule_head
    def _declaration(self):
        @rule
        def declaration(_parser):
            result = self._produce(self._type, self._ident_list, T.SEMICOLON)
            self._declare_variables(result)
            return result
        return declaration(self)

    @rule_head
    def _ident_list(self):
        @rule
        def ident_list(_parser):
            return self._produce(T.IDENT, self._resto_ident_list)
        return ident_list(self)

    @rule_head
    def _resto_ident_list(self):
        @rule
        def resto_ident_list(_parser):
            return self._produce(T.COMMA, T.IDENT, self._resto_ident_list)

        @rule
        def resto_ident_list_empty(_parser):
            return Result()

        if self.curr_token.type_ == T.COMMA:
            return resto_ident_list(self)
        return resto_ident_list_empty(self)

    @rule_head
    def _for_stmt(self):
        @rule(new_scope=True)
        def for_stmt(_parser):
            return self._produce(
                T.FOR, T.OPAR, self._opt_expr, T.SEMICOLON, self._opt_expr,
                T.SEMICOLON, self._opt_expr, T.CPAR, self._stmt)
        return for_stmt(self)

    @rule_head
    def _opt_expr(self):
        @rule
        def opt_expr(_parser):
            return self._produce(self._expr)

        @rule
        def opt_expr_empty(_parser):
            return Result()

        if self.curr_token.type_ in Parser._expr.first:
            return opt_expr(self)
        return opt_expr_empty(self)

    @rule_head
    def _io_stmt(self):
        @rule
        def io_stmt_scan(_parser):
            return self._produce(T.SCAN, T.OPAR, T.STR, T.COMMA, T.IDENT,
                                 T.CPAR, T.SEMICOLON)

        @rule
        def io_stmt_print(_parser):
            return self._produce(T.PRINT, T.OPAR, self._out_list, T.CPAR,
                                 T.SEMICOLON)

        if self.curr_token.type_ == T.SCAN:
            return io_stmt_scan(self)
        return io_stmt_print(self)

    @rule_head
    def _out_list(self):
        @rule
        def out_list(_parser):
            return self._produce(self._out, self._resto_out_list)
        return out_list(self)

    @rule_head
    def _out(self):
        @rule
        def out(_parser):
            return self._produce({T.NUMINT, T.NUMFLOAT, T.STR, T.IDENT})
        return out(self)

    @rule_head
    def _resto_out_list(self):
        @rule
        def resto_out_list(_parser):
            return self._produce(T.COMMA, self._out, self._resto_out_list)

        @rule
        def resto_out_list_empty(_parser):
            return Result()

        if self.curr_token.type_ == T.COMMA:
            return resto_out_list(self)
        return resto_out_list_empty(self)

    @rule_head
    def _while_stmt(self):
        @rule
        def while_stmt(_parser):
            return self._produce(T.WHILE, T.OPAR, self._expr, T.CPAR,
                                 self._stmt)
        return while_stmt(self)

    @rule_head
    def _if_stmt(self):
        @rule
        def if_stmt(_parser):
            return self._produce(T.IF, T.OPAR, self._expr, T.CPAR, self._stmt,
                                 self._else_part)
        return if_stmt(self)

    @rule_head
    def _else_part(self):
        @rule
        def else_part(_parser):
            return self._produce(T.ELSE, self._stmt)

        @rule
        def else_part_empty(_parser):
            return Result()

        if self.curr_token.type_ == T.ELSE:
            return else_part(self)
        return else_part_empty(self)

    @rule_head
    def _expr(self):
        @rule
        def expr(_parser):
            return self._produce(self._atrib)
        return expr(self)

    @rule_head
    def _atrib(self):
        def check_lvalue(results):
            if not results[0].lvalue and results[1].lvalue:
                self._error('Expression before = is not a lvalue.')

        @rule
        def atrib(_parser):
            return self._produce(self._or, self._resto_atrib,
                                 callback=check_lvalue)

        return atrib(self)

    @rule_head
    def _resto_atrib(self):
        @rule(lvalue=True)
        def resto_atrib(_parser):
            return self._produce(T.ASSIGN, self._atrib)

        @rule(lvalue=False)
        def resto_atrib_empty(_parser):
            return Result()

        if self.curr_token.type_ == T.ASSIGN:
            return resto_atrib(self)
        return resto_atrib_empty(self)

    @rule_head
    def _or(self):
        @rule
        def and_(_parser):
            return self._produce(self._and, self._resto_or)
        return and_(self)

    @rule_head
    def _resto_or(self):
        @rule(lvalue=False)
        def resto_or(_parser):
            return self._produce(T.OR, self._and, self._resto_or)

        @rule(lvalue=True)
        def resto_or_empty(_parser):
            return Result()

        if self.curr_token.type_ == T.OR:
            return resto_or(self)
        return resto_or_empty(self)

    @rule_head
    def _and(self):
        @rule
        def and_(_parser):
            return self._produce(self._not, self._resto_and)
        return and_(self)

    @rule_head
    def _resto_and(self):
        @rule(lvalue=False)
        def resto_and(_parser):
            return self._produce(T.AND, self._not, self._resto_and)

        @rule(lvalue=True)
        def resto_and_empty(_parser):
            return Result()

        if self.curr_token.type_ == T.AND:
            return resto_and(self)
        return resto_and_empty(self)

    @rule_head
    def _not(self):
        @rule(lvalue=False)
        def not_not(_parser):
            return self._produce(T.NOT, self._not)

        @rule
        def not_rel(_parser):
            return self._produce(self._rel)

        if self.curr_token.type_ == T.NOT:
            return not_not(self)
        return not_rel(self)

    @rule_head
    def _rel(self):
        @rule
        def rel(_parser):
            return self._produce(self._add, self._resto_rel)
        return rel(self)

    @rule_head
    def _resto_rel(self):
        @rule(lvalue=False)
        def resto_rel_eq(_parser):
            return self._produce(T.EQ, self._add)

        @rule(lvalue=False)
        def resto_rel_neq(_parser):
            return self._produce(T.NEQ, self._add)

        @rule(lvalue=False)
        def resto_rel_gt(_parser):
            return self._produce(T.GT, self._add)

        @rule(lvalue=False)
        def resto_rel_geq(_parser):
            return self._produce(T.GEQ, self._add)

        @rule(lvalue=False)
        def resto_rel_lt(_parser):
            return self._produce(T.LT, self._add)

        @rule(lvalue=False)
        def resto_rel_leq(_parser):
            return self._produce(T.LEQ, self._add)

        @rule(lvalue=True)
        def resto_rel_empty(_parser):
            return Result()

        if self.curr_token.type_ == T.EQ:
            return resto_rel_eq(self)
        if self.curr_token.type_ == T.NEQ:
            return resto_rel_neq(self)
        if self.curr_token.type_ == T.GT:
            return resto_rel_gt(self)
        if self.curr_token.type_ == T.GEQ:
            return resto_rel_geq(self)
        if self.curr_token.type_ == T.LT:
            return resto_rel_lt(self)
        if self.curr_token.type_ == T.LEQ:
            return resto_rel_leq(self)
        return resto_rel_empty(self)

    @rule_head
    def _add(self):
        @rule
        def add(_parser):
            return self._produce(self._mult, self._resto_add)
        return add(self)

    @rule_head
    def _resto_add(self):
        def resto_add(_parser, token_type):
            return self._produce(token_type, self._mult, self._resto_add)

        @rule(lvalue=False)
        def resto_add_plus(_parser):
            return resto_add(self, T.PLUS)

        @rule(lvalue=False)
        def resto_add_minus(_parser):
            return resto_add(self, T.MINUS)

        @rule(lvalue=True)
        def resto_add_empty(_parser):
            return Result()

        if self.curr_token.type_ == T.PLUS:
            return resto_add_plus(self)
        if self.curr_token.type_ == T.MINUS:
            return resto_add_minus(self)
        return resto_add_empty(self)

    @rule_head
    def _mult(self):
        @rule
        def mult(_parser):
            result = self._produce(self._uno, self._resto_mult)
            if result.operator == '%' and result.type_ != T.INT:
                self._error('% operands must be integer.')
            return result
        return mult(self)

    @rule_head
    def _resto_mult(self):
        @rule(lvalue=False)
        def resto_mult_mult(_parser):
            return self._produce(T.MULT, self._uno, self._resto_mult)

        @rule(lvalue=False)
        def resto_mult_div(_parser):
            return self._produce(T.DIV, self._uno, self._resto_mult)

        @rule(lvalue=False)
        def resto_mult_mod(_parser):
            result = self._produce(T.MOD, self._uno, self._resto_mult)
            if result.type_ != T.INT:
                self._error('% operands must be integer.')
            return result

        @rule(lvalue=True)
        def resto_mult_empty(_parser):
            return Result()

        if self.curr_token.type_ == T.MULT:
            return resto_mult_mult(self)
        if self.curr_token.type_ == T.DIV:
            return resto_mult_div(self)
        if self.curr_token.type_ == T.MOD:
            return resto_mult_mod(self)
        return resto_mult_empty(self)

    @rule_head
    def _uno(self):
        @rule(lvalue=False)
        def uno_plus(_parser):
            return self._produce(T.PLUS, self._uno)

        @rule(lvalue=False)
        def uno_minus(_parser):
            return self._produce(T.MINUS, self._uno)

        @rule
        def uno_fator(_parser):
            return self._produce(self._fator)

        if self.curr_token.type_ == T.PLUS:
            return uno_plus(self)
        if self.curr_token.type_ == T.MINUS:
            return uno_minus(self)
        return uno_fator(self)

    @rule_head
    def _fator(self):
        @rule(lvalue=True)
        def fator_ident(_parser):
            result = self._produce(T.IDENT)
            if result.type_ is None:
                self._error(f'Symbol {result.value[0][0]} not defined.')
            return result

        @rule(lvalue=False)
        def fator_num(_parser):
            return self._produce({T.NUMINT, T.NUMFLOAT})

        @rule(lvalue=False)
        def fator_atrib(_parser):
            return self._produce(T.OPAR, self._atrib, T.CPAR)

        if self.curr_token.type_ == T.OPAR:
            return fator_atrib(self)
        if self.curr_token.type_ == T.IDENT:
            return fator_ident(self)
        return fator_num(self)

    def _consume(self, expected):
        is_collection = isinstance(expected, Collection)
        found = self.curr_token.type_
        result = Result(lvalue=found == T.IDENT)
        if (is_collection and found in expected) or found == expected:
            if found == T.EOF:
                return result

            value = self.curr_token.typed_value
            if found == T.IDENT:
                result.type_ = self.symbol_table[value]
                depth = self.symbol_table.depth_of(value,
                                                   self.symbol_table.depth)
                result.value.append((value, depth))
            else:
                result.type_ = self.curr_token.data_type
                if value is not None:
                    result.value.append(value)

            result.operator = self.curr_token.operator

            self.tree.put_token(self.curr_token.name)
            self.curr_token = self.lexer.get_token()
        else:
            self._error(f'Expected {"one of " if is_collection else ""}'
                        f'{expected}, found {self.curr_token.name}.')
        return result

    def _produce(self, *args, callback: Callable = None) -> Result:
        results = []
        for symbol in args:
            if callable(symbol):
                results.append(symbol())
            else:
                results.append(self._consume(symbol))
        if callback is not None:
            callback(results)
        return sum(results)

    def _declare_variables(self, result: Result):
        for name, depth in result.value:
            full_name = f'__{depth}__{name}'
            if self.symbol_table.current_block_contains(full_name):
                self._error(f'Redeclaration of variable {name}')
            self.symbol_table[name] = result.type_

    def _error(self, msg):
        raise ParserError(f'Parser error: line {self.curr_token.row}, '
                          f'column {self.curr_token.col}: {msg}\n'
                          f'Stack: {self.tree.print_stack()}')
