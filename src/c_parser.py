from collections.abc import Collection
from enum import auto, Flag
from functools import partial, wraps
from typing import Callable

from c_code_generator import CodeGenerator
from c_grammar import FIRST, FOLLOW
from c_lexer import Lexer
from c_parser_result import Result
from c_parser_tree import ParserTree
from c_token import Token, TokenType


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


def rule(function=None, *, lvalue=None):
    if function is None:
        return partial(rule, lvalue=lvalue)

    method_name = f'{function.__name__.rstrip("_")}'
    pre_method_name = f'{method_name}_pre'

    def new_function(parser) -> Result:
        if ParserFeatures.CODE_GENERATION in parser.features:
            code_method = getattr(
                parser.code_generator, method_name,
                getattr(parser.code_generator, f'{method_name}_', None))
            pre_method = getattr(parser.code_generator, pre_method_name, None)

            if pre_method is not None:
                pre_method()
            result = code_method(function(parser))
        else:
            result = function(parser)

        if lvalue is not None:
            result.lvalue = lvalue
        return result

    return new_function


class ParserFeatures(Flag):
    NONE = 0
    TREE_DOT_GENERATION = auto()
    CODE_GENERATION = auto()
    DEFAULT = TREE_DOT_GENERATION | CODE_GENERATION


class Parser:
    def __init__(self, lexer: Lexer):
        self.curr_token: Token
        self.code_generator = CodeGenerator()
        self.features = ParserFeatures.DEFAULT
        self.lexer = lexer
        self.tree = ParserTree()
        self.symbol_table = {}

    def parse(self):
        self.curr_token = self.lexer.get_token()
        result = self._function()
        if ParserFeatures.TREE_DOT_GENERATION in self.features:
            with open('tree.dot', 'w') as file:
                file.write(str(self.tree))
        if ParserFeatures.CODE_GENERATION in self.features:
            with open('code.out', 'w') as file:
                file.write('\n'.join(str(c) for c in result.code[0][0]))

    @rule_head
    def _function(self):
        @rule
        def function(_parser):
            return self._produce(
                self._type, TokenType.IDENT, TokenType.OPAR, self._arg_list,
                TokenType.CPAR, self._bloco, TokenType.EOF)
        return function(self)

    @rule_head
    def _arg_list(self):
        @rule
        def arg_list(_parser):
            return self._produce(self._arg, self._resto_arg_list)

        @rule
        def arg_list_empty(_parser):
            return Result()

        if self.curr_token.id in Parser._arg_list.first:
            return arg_list(self)
        return arg_list_empty(self)

    @rule_head
    def _arg(self):
        @rule
        def arg(_parser):
            return self._produce(self._type, TokenType.IDENT)
        return arg(self)

    @rule_head
    def _resto_arg_list(self):
        @rule
        def resto_arg_list(_parser):
            return self._produce(TokenType.COMMA, self._arg_list)

        @rule
        def resto_arg_list_empty(_parser):
            return Result()

        if self.curr_token.id in Parser._resto_arg_list.first:
            return resto_arg_list(self)
        return resto_arg_list_empty(self)

    @rule_head
    def _type(self):
        @rule
        def type_(_parser):
            return self._produce({TokenType.INT, TokenType.FLOAT})
        return type_(self)

    @rule_head
    def _bloco(self):
        @rule
        def bloco(_parser):
            return self._produce(TokenType.OBRKT, self._stmt_list,
                                 TokenType.CBRKT)
        return bloco(self)

    @rule_head
    def _stmt_list(self):
        @rule
        def stmt_list(_parser):
            return self._produce(self._stmt, self._stmt_list)

        @rule
        def stmt_list_empty(_parser):
            return Result()

        if self.curr_token.id in Parser._stmt_list.first:
            return stmt_list(self)
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
        def stmt_declaration(_parser):
            return self._produce(self._declaration)

        @rule
        def stmt_expr(_parser):
            return self._produce(self._expr, TokenType.SEMICOLON)

        @rule
        def stmt_break(_parser):
            return self._produce(TokenType.BREAK, TokenType.SEMICOLON)

        @rule
        def stmt_continue(_parser):
            return self._produce(TokenType.CONTINUE, TokenType.SEMICOLON)

        @rule
        def stmt_return(_parser):
            return self._produce(TokenType.RETURN, self._fator,
                                 TokenType.SEMICOLON)

        @rule
        def stmt_null(_parser):
            return self._produce(TokenType.SEMICOLON)

        if self.curr_token.id in Parser._for_stmt.first:
            return stmt_for(self)
        if self.curr_token.id in Parser._io_stmt.first:
            return stmt_io(self)
        if self.curr_token.id in Parser._while_stmt.first:
            return stmt_while(self)
        if self.curr_token.id in Parser._if_stmt.first:
            return stmt_if(self)
        if self.curr_token.id in Parser._bloco.first:
            return stmt_bloco(self)
        if self.curr_token.id in Parser._declaration.first:
            return stmt_declaration(self)
        if self.curr_token.id in Parser._expr.first:
            return stmt_expr(self)
        if self.curr_token.id == TokenType.BREAK:
            return stmt_break(self)
        if self.curr_token.id == TokenType.CONTINUE:
            return stmt_continue(self)
        if self.curr_token.id == TokenType.RETURN:
            return stmt_return(self)
        return stmt_null(self)

    @rule_head
    def _declaration(self):
        @rule
        def declaration(_parser):
            result = self._produce(self._type, self._ident_list,
                                   TokenType.SEMICOLON)
            for name in result.value:
                self.symbol_table[name] = result.type_
            return result
        return declaration(self)

    @rule_head
    def _ident_list(self):
        @rule
        def ident_list(_parser):
            return self._produce(TokenType.IDENT, self._resto_ident_list)
        return ident_list(self)

    @rule_head
    def _resto_ident_list(self):
        @rule
        def resto_ident_list(_parser):
            return self._produce(TokenType.COMMA, TokenType.IDENT,
                                 self._resto_ident_list)

        @rule
        def resto_ident_list_empty(_parser):
            return Result()

        if self.curr_token.id == TokenType.COMMA:
            return resto_ident_list(self)
        return resto_ident_list_empty(self)

    @rule_head
    def _for_stmt(self):
        @rule
        def for_stmt(_parser):
            return self._produce(
                TokenType.FOR, TokenType.OPAR, self._opt_expr,
                TokenType.SEMICOLON, self._opt_expr, TokenType.SEMICOLON,
                self._opt_expr, TokenType.CPAR, self._stmt)
        return for_stmt(self)

    @rule_head
    def _opt_expr(self):
        @rule
        def opt_expr(_parser):
            return self._produce(self._expr)

        @rule
        def opt_expr_empty(_parser):
            return Result()

        if self.curr_token.id in Parser._expr.first:
            return opt_expr(self)
        return opt_expr_empty(self)

    @rule_head
    def _io_stmt(self):
        @rule
        def io_stmt_scan(_parser):
            return self._produce(
                TokenType.SCAN, TokenType.OPAR, TokenType.STR, TokenType.COMMA,
                TokenType.IDENT, TokenType.CPAR, TokenType.SEMICOLON)

        @rule
        def io_stmt_print(_parser):
            return self._produce(
                TokenType.PRINT, TokenType.OPAR, self._out_list,
                TokenType.CPAR, TokenType.SEMICOLON)

        if self.curr_token.id == TokenType.SCAN:
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
            return self._produce({TokenType.NUMINT, TokenType.NUMFLOAT,
                                  TokenType.STR, TokenType.IDENT})
        return out(self)

    @rule_head
    def _resto_out_list(self):
        @rule
        def resto_out_list(_parser):
            return self._produce(TokenType.COMMA, self._out,
                                 self._resto_out_list)

        @rule
        def resto_out_list_empty(_parser):
            return Result()

        if self.curr_token.id == TokenType.COMMA:
            return resto_out_list(self)
        return resto_out_list_empty(self)

    @rule_head
    def _while_stmt(self):
        @rule
        def while_stmt(_parser):
            return self._produce(TokenType.WHILE, TokenType.OPAR, self._expr,
                                 TokenType.CPAR, self._stmt)
        return while_stmt(self)

    @rule_head
    def _if_stmt(self):
        @rule
        def if_stmt(_parser):
            return self._produce(TokenType.IF, TokenType.OPAR, self._expr,
                                 TokenType.CPAR, self._stmt, self._else_part)
        return if_stmt(self)

    @rule_head
    def _else_part(self):
        @rule
        def else_part(_parser):
            return self._produce(TokenType.ELSE, self._stmt)

        @rule
        def else_part_empty(_parser):
            return Result()

        if self.curr_token.id == TokenType.ELSE:
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
            if results[0].lvalue and not results[1].lvalue:
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
            return self._produce(TokenType.ASSIGN, self._atrib)

        @rule(lvalue=False)
        def resto_atrib_empty(_parser):
            return Result()

        if self.curr_token.id == TokenType.ASSIGN:
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
            return self._produce(TokenType.OR, self._and, self._resto_or)

        @rule(lvalue=True)
        def resto_or_empty(_parser):
            return Result()

        if self.curr_token.id == TokenType.OR:
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
            return self._produce(TokenType.AND, self._not, self._resto_and)

        @rule(lvalue=True)
        def resto_and_empty(_parser):
            return Result()

        if self.curr_token.id == TokenType.AND:
            return resto_and(self)
        return resto_and_empty(self)

    @rule_head
    def _not(self):
        @rule(lvalue=False)
        def not_not(_parser):
            return self._produce(TokenType.NOT, self._not)

        @rule
        def not_rel(_parser):
            return self._produce(self._rel)

        if self.curr_token.id == TokenType.NOT:
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
            return self._produce(TokenType.EQ, self._add)

        @rule(lvalue=False)
        def resto_rel_neq(_parser):
            return self._produce(TokenType.NEQ, self._add)

        @rule(lvalue=False)
        def resto_rel_gt(_parser):
            return self._produce(TokenType.GT, self._add)

        @rule(lvalue=False)
        def resto_rel_geq(_parser):
            return self._produce(TokenType.GEQ, self._add)

        @rule(lvalue=False)
        def resto_rel_lt(_parser):
            return self._produce(TokenType.LT, self._add)

        @rule(lvalue=False)
        def resto_rel_leq(_parser):
            return self._produce(TokenType.LEQ, self._add)

        @rule(lvalue=True)
        def resto_rel_empty(_parser):
            return Result()

        if self.curr_token.id == TokenType.EQ:
            return resto_rel_eq(self)
        if self.curr_token.id == TokenType.NEQ:
            return resto_rel_neq(self)
        if self.curr_token.id == TokenType.GT:
            return resto_rel_gt(self)
        if self.curr_token.id == TokenType.GEQ:
            return resto_rel_geq(self)
        if self.curr_token.id == TokenType.LT:
            return resto_rel_lt(self)
        if self.curr_token.id == TokenType.LEQ:
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
            return resto_add(self, TokenType.PLUS)

        @rule(lvalue=False)
        def resto_add_minus(_parser):
            return resto_add(self, TokenType.MINUS)

        @rule(lvalue=True)
        def resto_add_empty(_parser):
            return Result()

        if self.curr_token.id == TokenType.PLUS:
            return resto_add_plus(self)
        if self.curr_token.id == TokenType.MINUS:
            return resto_add_minus(self)
        return resto_add_empty(self)

    @rule_head
    def _mult(self):
        @rule
        def mult(_parser):
            return self._produce(self._uno, self._resto_mult)
        return mult(self)

    @rule_head
    def _resto_mult(self):
        def resto_mult(_parser, token_type):
            return self._produce(token_type, self._uno, self._resto_mult)

        @rule(lvalue=False)
        def resto_mult_mult(_parser):
            return resto_mult(self, TokenType.MULT)

        @rule(lvalue=False)
        def resto_mult_div(_parser):
            return resto_mult(self, TokenType.DIV)

        @rule(lvalue=False)
        def resto_mult_mod(_parser):
            return resto_mult(self, TokenType.MOD)

        @rule(lvalue=True)
        def resto_mult_empty(_parser):
            return Result()

        if self.curr_token.id == TokenType.MULT:
            return resto_mult_mult(self)
        if self.curr_token.id == TokenType.DIV:
            return resto_mult_div(self)
        if self.curr_token.id == TokenType.MOD:
            return resto_mult_mod(self)
        return resto_mult_empty(self)

    @rule_head
    def _uno(self):
        @rule(lvalue=False)
        def uno_plus(_parser):
            return self._produce(TokenType.PLUS, self._uno)

        @rule(lvalue=False)
        def uno_minus(_parser):
            return self._produce(TokenType.MINUS, self._uno)

        @rule
        def uno_fator(_parser):
            return self._produce(self._fator)

        if self.curr_token.id == TokenType.PLUS:
            return uno_plus(self)
        if self.curr_token.id == TokenType.MINUS:
            return uno_minus(self)
        return uno_fator(self)

    @rule_head
    def _fator(self):
        @rule(lvalue=True)
        def fator_ident(_parser):
            return self._produce(TokenType.IDENT)

        @rule(lvalue=False)
        def fator_num(_parser):
            return self._produce({TokenType.NUMINT, TokenType.NUMFLOAT})

        @rule(lvalue=False)
        def fator_atrib(_parser):
            return self._produce(TokenType.OPAR, self._atrib, TokenType.CPAR)

        if self.curr_token.id == TokenType.OPAR:
            return fator_atrib(self)
        if self.curr_token.id == TokenType.IDENT:
            return fator_ident(self)
        return fator_num(self)

    def _consume(self, expected):
        is_collection = isinstance(expected, Collection)
        found = self.curr_token.id
        result = Result(lvalue=found == TokenType.IDENT)
        if (is_collection and found in expected) or found == expected:
            if found == TokenType.EOF:
                return result
            if found in (TokenType.INT, TokenType.FLOAT):
                result.type_ = found
            value = self.curr_token.value
            if value is not None:
                result.value.append(value)
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

    def _error(self, msg):
        raise ParserError(f'Parser error: line {self.curr_token.row}, '
                          f'column {self.curr_token.col}: {msg}\n'
                          f'Stack: {self.tree.print_stack()}')
