from sys import argv
from c_lexer import Lexer
from c_parser import Parser


class Intepreter:
    def __init__(self, fname: str):
        self.fname = fname
        self.lexer = Lexer(fname)
        self.parser = Parser(self.lexer)

    def run(self):
        self.parser.function()


def main():
    if (len(argv) <= 1):
        print('Falta nome do Arquivo')
        return

    intepreter = Intepreter(argv[1])
    intepreter.run()


if __name__ == "__main__":
    main()
