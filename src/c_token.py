from enum import auto, Enum


class TokenType(Enum):
    IDENT = auto()
    OPAR = auto()
    CPAR = auto()
    COMMA = auto()
    INT = auto()  # type
    FLOAT = auto()  # type
    OBRKT = auto()  # curly brackets
    CBRKT = auto()
    BREAK = auto()
    CONTINUE = auto()
    RETURN = auto()
    SEMICOLON = auto()
    FOR = auto()
    SCAN = auto()
    PRINT = auto()
    STR = auto()
    NUMINT = auto()
    NUMFLOAT = auto()
    WHILE = auto()
    IF = auto()
    ELSE = auto()
    EQUAL = auto()
    OR = auto()
    AND = auto()
    NOT = auto()
    LEQUAL = auto()
    LDIFF = auto()
    LESS = auto()
    LESSEQ = auto()
    BIGG = auto()
    BIGGEQ = auto()
    PLUS = auto()
    SUB = auto()
    MULT = auto()
    DIV = auto()
    MOD = auto()
    EOF = auto()
    ERR = auto()
    CMT = auto()
    NONE = auto()


_TOKEN_DICT = {
    '(': TokenType.OPAR,
    ')': TokenType.CPAR,
    ',': TokenType.COMMA,
    'int': TokenType.INT,
    'float': TokenType.FLOAT,
    '{': TokenType.OBRKT,
    '}': TokenType.CBRKT,
    'break': TokenType.BREAK,
    'continue': TokenType.CONTINUE,
    ';': TokenType.SEMICOLON,
    'for': TokenType.FOR,
    'scan': TokenType.SCAN,
    'print': TokenType.PRINT,
    'while': TokenType.WHILE,
    'if': TokenType.IF,
    'else': TokenType.ELSE,
    '=': TokenType.EQUAL,
    '||': TokenType.OR,
    '&&': TokenType.AND,
    '!': TokenType.NOT,
    '==': TokenType.LEQUAL,
    '!=': TokenType.LDIFF,
    '<': TokenType.LESS,
    '<=': TokenType.LESSEQ,
    '>': TokenType.BIGG,
    '>=': TokenType.BIGGEQ,
    '+': TokenType.PLUS,
    '-': TokenType.SUB,
    '*': TokenType.MULT,
    '/': TokenType.DIV,
    '%': TokenType.MOD,
    '//': TokenType.CMT,
    '/*': TokenType.CMT
}


class Token:
    def __init__(self, row=1, col=1, name='', id=-1):
        self.col = col
        self.row = row
        self.name = name
        self.id = id

    @staticmethod
    def get_token_type(key):
        return _TOKEN_DICT.get(key, None)

    def __str__(self):
        return "[" + str(self.row) + "," + str(self.col) + "] " + \
                str(self.id) + " - " + self.name
