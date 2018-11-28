from enum import auto, Enum, unique


@unique
class TokenType(Enum):
    IDENT = auto()
    STR = auto()
    EOF = auto()
    NUMINT = auto()
    NUMFLOAT = auto()
    OPAR = '('
    CPAR = ')'
    COMMA = ','
    INT = 'int'
    FLOAT = 'float'
    OBRKT = '{'
    CBRKT = '}'
    BREAK = 'break'
    CONTINUE = 'continue'
    RETURN = 'return'
    SEMICOLON = ';'
    FOR = 'for'
    SCAN = 'scan'
    PRINT = 'print'
    WHILE = 'while'
    IF = 'if'
    ELSE = 'else'
    ASSIGN = '='
    OR = '||'
    AND = '&&'
    NOT = '!'
    EQ = '=='
    NEQ = '!='
    LT = '<'
    LEQ = '<='
    GT = '>'
    GEQ = '>='
    PLUS = '+'
    MINUS = '-'
    MULT = '*'
    DIV = '/'
    MOD = '%'


class Token:
    OPERATORS = {TokenType.ASSIGN, TokenType.OR, TokenType.AND, TokenType}

    def __init__(self, row=1, col=1, name='', type_=None):
        self.col = col
        self.row = row
        self.name = name
        self.type_ = type_

    @property
    def data_type(self):
        if self.type_ == TokenType.NUMINT:
            return TokenType.INT
        if self.type_ == TokenType.NUMFLOAT:
            return TokenType.FLOAT
        if self.type_ in (TokenType.INT, TokenType.FLOAT):
            return self.type_
        return None

    @property
    def typed_value(self):
        if self.type_ == TokenType.NUMINT:
            return int(self.name)
        if self.type_ == TokenType.NUMFLOAT:
            return float(self.name)
        if self.type_ in (TokenType.STR, TokenType.IDENT):
            return self.name
        return None

    @property
    def operator(self):
        if self.type_ in {
                TokenType.ASSIGN, TokenType.OR, TokenType.AND, TokenType.NOT,
                TokenType.EQ, TokenType.NEQ, TokenType.LT, TokenType.LEQ,
                TokenType.GT, TokenType.GEQ, TokenType.PLUS, TokenType.MINUS,
                TokenType.MULT, TokenType.DIV, TokenType.MOD}:
            return self.type_.value
        return None

    @staticmethod
    def get_token_type(key):
        try:
            return TokenType(key)
        except ValueError:
            return None

    def __str__(self):
        return "[" + str(self.row) + "," + str(self.col) + "] " + \
                str(self.type_) + " - " + self.name
