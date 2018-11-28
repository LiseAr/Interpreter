from itertools import count


class SymbolTable:
    def __init__(self):
        self._stack = [{}]

    @property
    def depth(self):
        return len(self._stack) - 1

    def enter_block(self):
        self._stack.append({})

    def leave_block(self):
        self._stack.pop()

    def depth_of(self, symbol, default=None):
        stack = zip(count(len(self._stack) - 1, -1), reversed(self._stack))
        for i, table in stack:
            if symbol in table:
                return i
        if default is None:
            raise KeyError(f'{symbol} not found.')
        return default

    def __contains__(self, symbol):
        return self._stack and symbol in self._stack[-1]

    def __getitem__(self, key):
        if isinstance(key, tuple):
            raise IndexError('SymbolTable accepts only one key.')
        return next((d[key] for d in reversed(self._stack) if key in d), None)

    def __setitem__(self, key, value):
        self._stack[-1][key] = value
