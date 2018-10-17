from enum import auto, Enum
from c_token import Token, TokenType


class LexerError(Exception):
    pass


class File:
    def __init__(self, file_name):
        self.file_name = file_name
        self.line = ''
        self.file = open(file_name, 'r')

    def readline(self):
        self.line = self.file.readline()
        return self.line

    def close(self):  # TODO: close automatically
        self.file.close()


class State(Enum):
    INIT = auto()
    LET = auto()
    NUM = auto()
    NUMPTO = auto()
    PTONUM = auto()
    STR = auto()
    ENDSTR = auto()
    OPER = auto()
    OPER2 = auto()
    FIN = auto()
    ERR = auto()
    CMTB = auto()  # Comment Block
    SLSH = auto()  # Slash


class Symbol(Enum):
    LET = auto()
    NUM = auto()
    OPER = auto()
    INV = auto()
    PTO = auto()
    QMK = auto()  # Quotation Mark
    BKL = auto()  # Break Line
    SPACE = auto()
    UNDLN = auto()  # Underline
    SLSH = auto()  # Slash
    ASTK = auto()  # Asterisk


def symb_type(char):

    if char in {'+', '%', '=', '(', ')', ',', ';', '{',
                '}', '!', '>', '<', '|', '&', '-'}:
        return Symbol.OPER
    elif char == '_':
        return Symbol.UNDLN
    elif char == '/':
        return Symbol.SLSH
    elif char == '*':
        return Symbol.ASTK
    elif char == '.':
        return Symbol.PTO
    elif char == '\n':
        return Symbol.BKL
    elif char in {' ', '\t'}:
        return Symbol.SPACE
    elif char == '"':
        return Symbol.QMK
    elif 'a' <= char.lower() <= 'z':
        return Symbol.LET
    elif '0' <= char <= '9':
        return Symbol.NUM

    return Symbol.INV


TRANSITIONS = {
    State.INIT: {Symbol.LET: State.LET,
                 Symbol.UNDLN: State.LET,
                 Symbol.NUM: State.NUM,
                 Symbol.PTO: State.NUMPTO,
                 Symbol.OPER: State.OPER,
                 Symbol.ASTK: State.OPER,
                 Symbol.SPACE: State.INIT,
                 Symbol.BKL: State.INIT,
                 Symbol.QMK: State.STR,
                 Symbol.SLSH: State.SLSH},

    # nesse estado se constroi identificadores e palavras reservadas
    State.LET: {Symbol.LET: State.LET,
                Symbol.NUM: State.LET,
                Symbol.UNDLN: State.LET,
                Symbol.OPER: State.FIN,
                Symbol.SPACE: State.FIN,
                Symbol.BKL: State.FIN,
                Symbol.QMK: State.FIN,
                Symbol.SLSH: State.FIN,
                Symbol.ASTK: State.FIN},


    State.NUM: {Symbol.LET: State.FIN,
                Symbol.NUM: State.NUM,
                Symbol.OPER: State.FIN,
                Symbol.SPACE: State.FIN,
                Symbol.BKL: State.FIN,
                Symbol.QMK: State.FIN,
                Symbol.PTO: State.NUMPTO,
                Symbol.SLSH: State.FIN,
                Symbol.ASTK: State.FIN,
                Symbol.UNDLN: State.FIN},

    State.NUMPTO: {Symbol.NUM: State.PTONUM},

    State.PTONUM: {Symbol.LET: State.FIN,
                   Symbol.NUM: State.PTONUM,
                   Symbol.OPER: State.FIN,
                   Symbol.SPACE: State.FIN,
                   Symbol.BKL: State.FIN,
                   Symbol.QMK: State.FIN,
                   Symbol.PTO: State.FIN,
                   Symbol.SLSH: State.FIN,
                   Symbol.ASTK: State.FIN,
                   Symbol.UNDLN: State.FIN},

    State.STR: {Symbol.LET: State.STR,
                Symbol.NUM: State.STR,
                Symbol.OPER: State.STR,
                Symbol.SPACE: State.STR,
                Symbol.BKL: State.STR,
                Symbol.QMK: State.ENDSTR,
                Symbol.INV: State.STR,
                Symbol.PTO: State.STR,
                Symbol.SLSH: State.STR,
                Symbol.ASTK: State.STR,
                Symbol.UNDLN: State.STR},

    State.SLSH: {Symbol.LET: State.FIN,
                 Symbol.UNDLN: State.FIN,
                 Symbol.NUM: State.FIN,
                 Symbol.PTO: State.FIN,
                 Symbol.OPER: State.FIN,
                 Symbol.ASTK: State.CMTB,
                 Symbol.SPACE: State.FIN,
                 Symbol.BKL: State.FIN,
                 Symbol.QMK: State.FIN,
                 Symbol.SLSH: State.INIT},

    State.OPER: {Symbol.LET: State.FIN,
                 Symbol.NUM: State.FIN,
                 Symbol.OPER: State.OPER2,
                 Symbol.SPACE: State.FIN,
                 Symbol.BKL: State.FIN,
                 Symbol.QMK: State.FIN,
                 Symbol.PTO: State.FIN,
                 Symbol.SLSH: State.FIN,
                 Symbol.ASTK: State.FIN,
                 Symbol.UNDLN: State.FIN},

    State.OPER2: {Symbol.LET: State.FIN,
                  Symbol.NUM: State.FIN,
                  Symbol.OPER: State.FIN,
                  Symbol.SPACE: State.FIN,
                  Symbol.BKL: State.FIN,
                  Symbol.QMK: State.FIN,
                  Symbol.PTO: State.FIN,
                  Symbol.SLSH: State.FIN,
                  Symbol.ASTK: State.FIN,
                  Symbol.UNDLN: State.FIN},

    State.ENDSTR: {Symbol.LET: State.FIN,
                   Symbol.NUM: State.FIN,
                   Symbol.OPER: State.FIN,
                   Symbol.SPACE: State.FIN,
                   Symbol.BKL: State.FIN,
                   Symbol.QMK: State.FIN,
                   Symbol.INV: State.FIN,
                   Symbol.PTO: State.FIN,
                   Symbol.SLSH: State.FIN,
                   Symbol.ASTK: State.FIN,
                   Symbol.UNDLN: State.FIN}
}


class Lexer:
    def __init__(self, fname: str):
        self._file = File(fname)
        self.row = 1
        self.col = 1
        self.buffer = ''

    def _error(self, msg):
        raise LexerError(f'Parser error: line {self.row}, '
                         f'column {self.col}: {msg}')

    def get_token(self):

        if self._file.line == '':
            line = self._file.readline()
        else:
            line = self._file.line

        current_state = State.INIT
        self.buffer = ''

        while True:
            symb = symb_type(line[0])
            previous_state = current_state
            current_state = TRANSITIONS[previous_state].get(symb, State.ERR)

            if current_state not in {State.INIT, State.FIN, State.ERR}:
                if current_state == State.CMTB:
                    while line.find('*/') == -1:
                        line = self._file.readline()
                        self.row += 1
                    line = self._file.readline()
                    self.row += 1
                    self.buffer = ''
                    self.col = 1
                    previous_state = current_state = State.INIT
                elif (current_state != State.OPER2 or
                      Token.get_token_type(self.buffer + line[0]) is not None):
                    self.buffer = self.buffer + line[0]
                    line = line[1:]
                    self.col += 1
                else:
                    current_state = State.FIN

            if current_state == State.INIT:
                if symb == Symbol.SPACE:
                    line = line[1:]
                    self.col += 1
                elif symb == Symbol.BKL or previous_state == State.SLSH:
                    self.buffer = ''
                    line = self._file.readline()
                    self.row += 1
                    self.col = 1

            elif current_state == State.FIN:
                token_id = None
                if previous_state in {State.LET, State.OPER, State.OPER2,
                                      State.SLSH}:
                    token_id = Token.get_token_type(self.buffer)
                    if token_id is None:
                        token_id = TokenType.IDENT
                elif previous_state is State.NUM:
                    token_id = TokenType.NUMINT
                elif previous_state is State.PTONUM:
                    token_id = TokenType.NUMFLOAT
                elif previous_state in {State.STR, State.ENDSTR}:
                    token_id = TokenType.STR
                self._file.line = line
                return Token(self.row, self.col - len(self.buffer),
                             self.buffer, token_id)

            elif current_state == State.ERR:
                self.buffer += line[0]
                self._error(f'Invalid token {self.buffer}')

            if line == '':
                line = self._file.readline()
                self.col = 1
            if line == '':
                return Token(self.row, self.col - len(self.buffer),
                             'EOF', TokenType.EOF)
