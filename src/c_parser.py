from functools import wraps

from c_lexer import Lexer
from c_parser_tree import ParserTree
from c_token import Token, TokenType


class ParserError(Exception):
    pass


class Result:
    def __init__(self, lvalue: bool = None):
        self.lvalue = lvalue


def rule(func):
    @wraps(func)
    def _newfunc(self):
        self.tree.push(func.__name__)
        result = func(self)
        self.tree.pop()
        return result
    return _newfunc


class Parser:
    def __init__(self, lexer: Lexer):
        self.curr_token: Token
        self.lexer = lexer
        self.tree = ParserTree()

    def parse(self):
        self._function()
        with open('tree.dot', 'w') as file:
            file.write(str(self.tree))

    def _error(self, msg):
        raise ParserError(f'Parser error: line {self.curr_token.row}, '
                          f'column {self.curr_token.col}: {msg}')

    @rule
    def _function(self):
        self.curr_token = self.lexer.get_token()
        self._type()
        self._consome(TokenType.IDENT)
        self._consome(TokenType.OPAR)
        self._arg_list()
        self._consome(TokenType.CPAR)
        self._bloco()
        self._consome(TokenType.EOF)

    @rule
    def _arg_list(self):
        if self.curr_token.id in {TokenType.INT, TokenType.FLOAT}:
            self._arg()
            self._resto_arg_list()

    @rule
    def _arg(self):
        self._type()
        self._consome(TokenType.IDENT)

    @rule
    def _resto_arg_list(self):
        if self.curr_token.name[0] == TokenType.COMMA:
            self._consome(TokenType.COMMA)
            self._arg_list()

    @rule
    def _type(self):
        self._consome(self.curr_token.id)

    @rule
    def _bloco(self):
        self._consome(TokenType.OBRKT)
        self._stmt_list()
        self._consome(TokenType.CBRKT)

    @rule
    def _stmt_list(self):
        if self.curr_token.id in {TokenType.NOT, TokenType.OPAR,
                                  TokenType.PLUS, TokenType.SUB,
                                  TokenType.SEMICOLON, TokenType.IDENT,
                                  TokenType.NUMFLOAT, TokenType.NUMINT,
                                  TokenType.BREAK, TokenType.CONTINUE,
                                  TokenType.FLOAT, TokenType.FOR,
                                  TokenType.IF, TokenType.INT, TokenType.PRINT,
                                  TokenType.SCAN, TokenType.WHILE,
                                  TokenType.OBRKT}:
            self._stmt()
            self._stmt_list()

    @rule
    def _stmt(self):
        if self.curr_token.id == TokenType.FOR:
            self._for_stmt()
        elif self.curr_token.id in {TokenType.SCAN, TokenType.PRINT}:
            self._io_stmt()
        elif self.curr_token.id == TokenType.WHILE:
            self._while_stmt()
        elif self.curr_token.id == TokenType.IF:
            self._if_stmt()
        elif self.curr_token.id == TokenType.OBRKT:
            self._bloco()
        elif self.curr_token.id == TokenType.BREAK:
            self._consome(TokenType.BREAK)
            self._consome(TokenType.SEMICOLON)
        elif self.curr_token.id == TokenType.CONTINUE:
            self._consome(TokenType.CONTINUE)
            self._consome(TokenType.SEMICOLON)
        elif self.curr_token.id == TokenType.RETURN:
            self._consome(TokenType.RETURN)
            self._fator()
            self._consome(TokenType.SEMICOLON)
        elif self.curr_token.id in {TokenType.INT, TokenType.FLOAT}:
            self._declaration()
        elif self.curr_token.id == TokenType.SEMICOLON:
            self._consome(TokenType.SEMICOLON)
        elif self.curr_token.id in {TokenType.NOT, TokenType.OPAR,
                                    TokenType.PLUS, TokenType.SUB,
                                    TokenType.IDENT, TokenType.NUMFLOAT,
                                    TokenType.NUMINT}:
            self._expr()
            self._consome(TokenType.SEMICOLON)

    # ---------------------------
    # descricao das instrucoes
    # ---------------------------

    @rule
    def _declaration(self):
        self._type()
        self._ident_list()
        self._consome(TokenType.SEMICOLON)

    @rule
    def _ident_list(self):
        self._consome(TokenType.IDENT)
        self._resto_ident_list()

    @rule
    def _resto_ident_list(self):
        if self.curr_token.id == TokenType.COMMA:
            self._consome(TokenType.COMMA)
            self._consome(TokenType.IDENT)
            self._resto_ident_list()

    @rule
    def _for_stmt(self):
        self._consome(TokenType.FOR)
        self._consome(TokenType.OPAR)
        self._opt_exp()
        self._consome(TokenType.SEMICOLON)
        self._opt_exp()
        self._consome(TokenType.SEMICOLON)
        self._opt_exp()
        self._consome(TokenType.CPAR)
        self._stmt()

    @rule
    def _opt_exp(self):
        if self.curr_token.id in {TokenType.NOT, TokenType.OPAR,
                                  TokenType.PLUS, TokenType.SUB,
                                  TokenType.IDENT, TokenType.NUMFLOAT,
                                  TokenType.NUMINT}:
            self._expr()

    @rule
    def _io_stmt(self):
        if self.curr_token.id == TokenType.SCAN:
            self._consome(TokenType.SCAN)
            self._consome(TokenType.OPAR)
            self._consome(TokenType.STR)
            self._consome(TokenType.COMMA)
            self._consome(TokenType.IDENT)
        elif self.curr_token.id == TokenType.PRINT:
            self._consome(TokenType.PRINT)
            self._consome(TokenType.OPAR)
            self._out_list()
        self._consome(TokenType.CPAR)
        self._consome(TokenType.SEMICOLON)

    @rule
    def _out_list(self):
        self._out()
        self._resto_out_list()

    @rule
    def _out(self):
        self._consome(self.curr_token.id)

    @rule
    def _resto_out_list(self):
        if self.curr_token.id == TokenType.COMMA:
            self._consome(TokenType.COMMA)
            self._out()
            self._resto_out_list()

    @rule
    def _while_stmt(self):
        self._consome(TokenType.WHILE)
        self._consome(TokenType.OPAR)
        self._expr()
        self._consome(TokenType.CPAR)
        self._stmt()

    @rule
    def _if_stmt(self):
        self._consome(TokenType.IF)
        self._consome(TokenType.OPAR)
        self._expr()
        self._consome(TokenType.CPAR)
        self._stmt()
        self._else_part()

    @rule
    def _else_part(self):
        if self.curr_token.id == TokenType.ELSE:
            self._consome(TokenType.ELSE)
            self._stmt()

    # ------------------------------
    # expressoes
    # ------------------------------

    @rule
    def _expr(self):
        self._atrib()

    @rule
    def _atrib(self):
        l_result = self._or()
        r_result = self._resto_atrib()
        if r_result.lvalue and not l_result.lvalue:
            self._error('Expression before = is not a lvalue.')

    @rule
    def _resto_atrib(self):
        if self.curr_token.id == TokenType.EQUAL:
            self._consome(TokenType.EQUAL)
            self._atrib()
            return Result(True)
        return Result(False)

    @rule
    def _or(self):
        results = []
        results.append(self._and())
        results.append(self._resto_or())
        return Result(all(r.lvalue for r in results))

    @rule
    def _resto_or(self):
        if self.curr_token.id == TokenType.OR:
            self._consome(TokenType.OR)
            self._and()
            self._resto_or()
            return Result(False)
        return Result(True)

    @rule
    def _and(self):
        results = []
        results.append(self._not())
        results.append(self._resto_and())
        return Result(all(r.lvalue for r in results))

    @rule
    def _resto_and(self):
        if self.curr_token.id == TokenType.AND:
            self._consome(TokenType.AND)
            self._not()
            self._resto_and()
            return Result(False)
        return Result(True)

    @rule
    def _not(self):
        if self.curr_token.id == TokenType.NOT:
            self._consome(TokenType.NOT)
            self._not()
            return Result(False)
        else:
            return self._rel()

    @rule
    def _rel(self):
        results = []
        results.append(self._add())
        results.append(self._resto_rel())
        return Result(all(r.lvalue for r in results))

    @rule
    def _resto_rel(self):
        if self.curr_token.id in {TokenType.LEQUAL, TokenType.LDIFF,
                                  TokenType.LESS, TokenType.LESSEQ,
                                  TokenType.BIGG, TokenType.BIGGEQ}:
            self._consome(self.curr_token.id)
            self._add()
            return Result(False)
        return Result(True)

    @rule
    def _add(self):
        results = []
        results.append(self._mult())
        results.append(self._resto_add())
        return Result(all(r.lvalue for r in results))

    @rule
    def _resto_add(self):
        if self.curr_token.id in {TokenType.PLUS, TokenType.SUB}:
            self._consome(self.curr_token.id)
            self._mult()
            self._resto_add()
            return Result(False)
        return Result(True)

    @rule
    def _mult(self):
        results = []
        results.append(self._uno())
        results.append(self._resto_mult())
        return Result(all(r.lvalue for r in results))

    @rule
    def _resto_mult(self):
        if self.curr_token.id in {TokenType.MULT, TokenType.DIV,
                                  TokenType.MOD}:
            self._consome(self.curr_token.id)
            self._uno()
            self._resto_mult()
            return Result(False)
        return Result(True)

    @rule
    def _uno(self):
        if self.curr_token.id in {TokenType.PLUS, TokenType.SUB}:
            self._consome(self.curr_token.id)
            return self._uno()
        else:
            return self._fator()

    @rule
    def _fator(self):
        if self.curr_token.id in {TokenType.NUMINT, TokenType.NUMFLOAT,
                                  TokenType.IDENT}:
            result = Result(self.curr_token.id == TokenType.IDENT)
            self._consome(self.curr_token.id)
            return result
        else:
            self._consome(TokenType.OPAR)
            self._atrib()
            self._consome(TokenType.CPAR)
            return Result(False)

    def _consome(self, tok):
        if self.curr_token.id == tok:
            if self.curr_token.id == TokenType.EOF:
                return
            else:
                self.curr_token = self.lexer.get_token()
        else:
            self._error(f'expected {tok} found {self.curr_token.name}')
