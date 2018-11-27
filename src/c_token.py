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
    def __init__(self, row=1, col=1, name='', id=-1):
        self.col = col
        self.row = row
        self.name = name
        self.id = id

    @property
    def value(self):
        if self.id == TokenType.NUMINT:
            return int(self.name)
        if self.id == TokenType.NUMFLOAT:
            return float(self.name)
        if self.id in (TokenType.STR, TokenType.IDENT):
            return self.name
        return None

    @staticmethod
    def get_token_type(key):
        try:
            return TokenType(key)
        except ValueError:
            return None

    def __str__(self):
        return "[" + str(self.row) + "," + str(self.col) + "] " + \
                str(self.id) + " - " + self.name
