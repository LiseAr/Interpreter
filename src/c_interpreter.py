from sys import argv
from c_lexer import Lexer, LexerError
from c_parser import Parser, ParserError


class Intepreter:
    def __init__(self, fname: str):
        self.fname = fname
        self.lexer = Lexer(fname)
        self.parser = Parser(self.lexer)

    def run(self):
        try:
            self.parser.function()
        except (LexerError, ParserError) as exception:
            print(exception)


def main():
    if len(argv) <= 1:
        print('Falta nome do Arquivo')
        return

    intepreter = Intepreter(argv[1])
    intepreter.run()


if __name__ == "__main__":
    main()
