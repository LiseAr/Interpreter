from itertools import count


class ParserTree:
    def __init__(self):
        self._node_count = count()
        self._call_stack = []
        self._edges = []
        self._labels = {}

    def push(self, name: str):
        identifier = f'{name}{next(self._node_count)}'
        label = f'<{name.strip("_")}>'
        self._labels[identifier] = label
        self._call_stack.append(identifier)
        if len(self._call_stack) >= 2:
            self._edges.append(tuple(self._call_stack[-2:]))

    def pop(self):
        self._call_stack.pop()

    def __str__(self):
        return '\n'.join([
            'graph {',
            '\n'.join(f'{i} [label="{l}"];' for i, l in self._labels.items()),
            '\n'.join(' -- '.join(e) for e in self._edges),
            '}'
        ])
