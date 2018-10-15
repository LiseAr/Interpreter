from c_lexer import Lexer
from c_token import Token, TokenType


class Parser:
    def __init__(self, lexer: Lexer):
        self.curr_token: Token
        self.lexer = lexer

    def function(self):
        self.curr_token = self.lexer.get_token()
        '''
        print(self.curr_token)
        while self.curr_token.id != TokenType.EOF:
           self.curr_token = self.lexer.get_token()
           print(self.curr_token)
        '''
        self.type()
        self.consome(TokenType.IDENT)
        self.consome(TokenType.OPAR)
        self.arg_list()
        self.consome(TokenType.CPAR)
        self.bloco()
        self.consome(TokenType.EOF)

    def arg_list(self):
        if self.curr_token.id in {TokenType.INT, TokenType.FLOAT}:
            self.arg()
            self.resto_arg_list()

    def arg(self):
        self.type()
        self.consome(TokenType.IDENT)

    def resto_arg_list(self):
        if self.curr_token.name[0] == TokenType.COMMA:
            self.consome(TokenType.COMMA)
            self.arg_list()

    def type(self):
        self.consome(self.curr_token.id)

    def bloco(self):
        self.consome(TokenType.OBRKT)
        self.stmt_list()
        self.consome(TokenType.CBRKT)

    def stmt_list(self):
        if self.curr_token.id in {TokenType.NOT, TokenType.OPAR,
                                  TokenType.PLUS, TokenType.SUB,
                                  TokenType.SEMICOLON, TokenType.IDENT,
                                  TokenType.NUMFLOAT, TokenType.NUMINT,
                                  TokenType.BREAK, TokenType.CONTINUE,
                                  TokenType.FLOAT, TokenType.FOR,
                                  TokenType.IF, TokenType.INT, TokenType.PRINT,
                                  TokenType.SCAN, TokenType.WHILE,
                                  TokenType.OBRKT}:
            self.stmt()
            self.stmt_list()

    def stmt(self):
        if self.curr_token.id == TokenType.FOR:
            self.for_stmt()
        elif self.curr_token.id in {TokenType.SCAN, TokenType.PRINT}:
            self.io_stmt()
        elif self.curr_token.id == TokenType.WHILE:
            self.while_stmt()
        elif self.curr_token.id == TokenType.IF:
            self.if_stmt()
        elif self.curr_token.id == TokenType.OBRKT:
            self.bloco()
        elif self.curr_token.id == 'break':
            self.consome(TokenType.BREAK)
        elif self.curr_token.id == 'continue':
            self.consome(TokenType.CONTINUE)
        elif self.curr_token.id in {TokenType.INT, TokenType.FLOAT}:
            self.declaration()
        elif self.curr_token.id == TokenType.SEMICOLON:
            self.consome(TokenType.SEMICOLON)
        elif self.curr_token.id in {TokenType.NOT, TokenType.OPAR,
                                    TokenType.PLUS, TokenType.SUB,
                                    TokenType.IDENT, TokenType.NUMFLOAT,
                                    TokenType.NUMINT}:
            self.expr()
            self.consome(TokenType.SEMICOLON)

    # ---------------------------
    # descricao das instrucoes
    # ---------------------------

    def declaration(self):
        self.type()
        self.ident_list()
        self.consome(TokenType.SEMICOLON)

    def ident_list(self):
        self.consome(TokenType.IDENT)
        self.resto_ident_list()

    def resto_ident_list(self):
        if self.curr_token.id == TokenType.COMMA:
            self.consome(TokenType.COMMA)
            self.consome(TokenType.IDENT)
            self.resto_ident_list()

    def for_stmt(self):
        self.consome(TokenType.FOR)
        self.consome(TokenType.OPAR)
        self.opt_exp()
        self.consome(TokenType.SEMICOLON)
        self.opt_exp()
        self.consome(TokenType.SEMICOLON)
        self.opt_exp()
        self.consome(TokenType.CPAR)
        self.stmt()

    def opt_exp(self):
        if self.curr_token.id in {TokenType.NOT, TokenType.OPAR,
                                  TokenType.PLUS, TokenType.SUB,
                                  TokenType.IDENT, TokenType.NUMFLOAT,
                                  TokenType.NUMINT}:
            self.expr()

    def io_stmt(self):
        if self.curr_token.id == TokenType.SCAN:
            self.consome(TokenType.SCAN)
            self.consome(TokenType.OPAR)
            self.consome(TokenType.IDENT)
            # self.out_list()
        elif self.curr_token.id == TokenType.PRINT:
            self.consome(TokenType.PRINT)
            self.consome(TokenType.OPAR)
            self.out_list()
        self.consome(TokenType.CPAR)
        self.consome(TokenType.SEMICOLON)

    def out_list(self):
        self.out()
        self.resto_out_list()

    def out(self):
        self.consome(self.curr_token.id)

    def resto_out_list(self):
        if self.curr_token.id == TokenType.COMMA:
            self.consome(TokenType.COMMA)
            self.out()
            self.resto_out_list()

    def while_stmt(self):
        self.consome(TokenType.WHILE)
        self.consome(TokenType.OPAR)
        self.expr()
        self.consome(TokenType.CPAR)
        self.stmt()

    def if_stmt(self):
        self.consome(TokenType.IF)
        self.consome(TokenType.OPAR)
        self.expr()
        self.consome(TokenType.CPAR)
        self.stmt()
        self.else_part()

    def else_part(self):
        if self.curr_token.id == TokenType.ELSE:
            self.consome(TokenType.ELSE)
            self.stmt()

    # ------------------------------
    # expressoes
    # ------------------------------

    def expr(self):
        self.atrib()

    def atrib(self):
        self.or_()
        self.resto_atrib()

    def resto_atrib(self):
        if self.curr_token.id == TokenType.EQUAL:
            self.consome(TokenType.EQUAL)
            self.atrib()

    def or_(self):
        self.and_()
        self.resto_or()

    def resto_or(self):
        if (self.curr_token.id == TokenType.OR):
            self.consome(TokenType.OR)
            self.and_()
            self.resto_or()

    def and_(self):
        self.not_()
        self.resto_and()

    def resto_and(self):
        if self.curr_token.id == TokenType.AND:
            self.consome(TokenType.AND)
            self.not_()
            self.resto_and()

    def not_(self):
        if self.curr_token.id == TokenType.NOT:
            self.consome(TokenType.NOT)
            self.not_()
        else:
            self.rel()

    def rel(self):
        self.add()
        self.resto_rel()

    def resto_rel(self):
        if self.curr_token.id in {TokenType.LEQUAL, TokenType.LDIFF,
                                  TokenType.LESS, TokenType.LESSEQ,
                                  TokenType.BIGG, TokenType.BIGGEQ}:
            self.consome(self.curr_token.id)
            self.add()

    def add(self):
        self.mult()
        self.resto_add()

    def resto_add(self):
        if self.curr_token.id in [TokenType.PLUS, TokenType.SUB]:
            self.consome(self.curr_token.id)
            self.mult()
            self.resto_add()

    def mult(self):
        self.uno()
        self.resto_mult()

    def resto_mult(self):
        if self.curr_token.id in [TokenType.MULT, TokenType.DIV,
                                  TokenType.MOD]:
            self.consome(self.curr_token.id)
            self.uno()
            self.resto_mult()

    def uno(self):
        if self.curr_token.id in [TokenType.PLUS, TokenType.SUB]:
            self.consome(self.curr_token.id)
            self.uno()
        else:
            self.fator()

    def fator(self):
        if self.curr_token.id in [TokenType.NUMINT, TokenType.NUMFLOAT,
                                  TokenType.IDENT]:
            self.consome(self.curr_token.id)
        else:
            self.consome(TokenType.OPAR)
            self.atrib()
            self.consome(TokenType.CPAR)

    def consome(self, tok):
        if (self.curr_token.id == tok):
            if self.curr_token.id == TokenType.EOF:
                return
            else:
                self.curr_token = self.lexer.get_token()
        else:
            raise Exception(
                f'Parser error: line {self.curr_token.row}, '
                f'column {self.curr_token.col}: '
                f'expected {tok} found {self.curr_token.name}')
