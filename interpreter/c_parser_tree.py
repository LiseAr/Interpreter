# -*- coding: utf-8 -*-

from itertools import count


class ParserTree:
    def __init__(self):
        self._node_count = count()
        self._call_stack = []
        self._edges = []
        self._labels = {}
        self._xlabels = {}

    def push(self, name: str):
        identifier = (name, str(next(self._node_count)))
        label = f'〈{name}〉'
        self._labels[''.join(identifier)] = label
        self._call_stack.append(identifier)
        if len(self._call_stack) >= 2:
            self._edges.append(tuple(self._call_stack[-2:]))

    def pop(self):
        self._call_stack.pop()

    def print_stack(self):
        return ' -> '.join(s[0] for s in self._call_stack)

    def put_token(self, token: str):
        xlabels = self._xlabels.setdefault(''.join(self._call_stack[-1]), [])
        xlabels.append(token)

    def __str__(self):
        def _xlabel(ident):
            xlabels = self._xlabels.get(ident, None)
            if not xlabels:
                return ''
            xlabel = ' '.join(xlabels).replace('<', '〈').replace('>', '〉')
            return f'<BR/><BR/><b>{xlabel}</b>'

        return '\n'.join([
            'graph {',
            '\n'.join(f'{i} [label=<{l}{_xlabel(i)}>];'
                      for i, l in self._labels.items()),
            '\n'.join(' -- '.join(e) for e in
                      ((''.join(v[0]), ''.join(v[1])) for v in self._edges)),
            '}'
        ])
