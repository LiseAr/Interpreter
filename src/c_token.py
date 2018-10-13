from enum import Enum


class TokenType(Enum):
    IDENT = 0
    OPAR = 1
    CPAR = 2
    COMMA = 3
    INT = 4  # type
    FLOAT = 5  # type
    OBRKT = 6  # curly brackets
    CBRKT = 7
    BREAK = 8
    CONTINUE = 9
    SEMICOLON = 10
    FOR = 11
    SCAN = 12
    PRINT = 13
    STR = 14
    NUMINT = 15
    NUMFLOAT = 16
    WHILE = 17
    IF = 18
    ELSE = 19
    EQUAL = 20
    OR = 21
    AND = 22
    NOT = 23
    LEQUAL = 24
    LDIFF = 25
    LESS = 26
    LESSEQ = 27
    BIGG = 28
    BIGGEQ = 29
    PLUS = 30
    SUB = 31
    MULT = 32
    DIV = 33
    MOD = 34
    EOF = 35
    ERR = 36
    CMT = 37
    NONE = 38


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
