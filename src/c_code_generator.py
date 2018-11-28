from collections import namedtuple
from itertools import count

from c_parser_result import Result
from c_instruction import Instruction


LoopLabels = namedtuple('LoopLabels', ['break_', 'continue_'])


def name_generator(prefix: str):
    for i in count(1):
        yield f'{prefix}{i}'


class CodeGenerator:
    def __init__(self):
        self._label_gen = name_generator('__label__')
        self._temp_gen = name_generator('__temp__')
        self._expression_result = None
        self._return_label = self._generate_label()
        self._loop_stack = []

    def _generate_label(self):
        return next(self._label_gen)

    def _generate_temp(self):
        return next(self._temp_gen)

    def function(self, result: Result) -> Result:
        """<function> -> <type> 'IDENT' '(' <argList> ')' <bloco>"""
        return result

    def arg_list(self, result: Result) -> Result:
        """<argList> -> <arg> <restoArgList>"""
        return result

    def arg_list_empty(self, result: Result) -> Result:
        """<argList> -> &"""
        return result

    def arg(self, result: Result) -> Result:
        """<arg> -> <type> 'IDENT'"""
        return result

    def resto_arg_list(self, result: Result) -> Result:
        """<restoArgList> -> ',' <argList>"""
        return result

    def resto_arg_list_empty(self, result: Result) -> Result:
        """<restoArgList> -> ',' <argList>"""
        return result

    def type_(self, result: Result) -> Result:
        """<type> -> 'int' | 'float'"""
        return result

    def bloco(self, result: Result) -> Result:
        """<bloco> -> '{' <stmtList> '}'"""
        return result

    def stmt_list(self, result: Result) -> Result:
        """<stmtList> -> <stmt> <stmtList>"""
        stmt_list_code = result.code.pop()[0]
        code = result.code.pop()[0]
        code.extend(stmt_list_code)
        result.code.append((code, None))
        return result

    def stmt_list_empty(self, result: Result) -> Result:
        """<stmtList> -> &"""
        result.code.append(([], None))
        return result

    def stmt_for(self, result: Result) -> Result:
        """<stmt> -> <forStmt>"""
        return result

    def stmt_io(self, result: Result) -> Result:
        """<stmt> -> <ioStmt>"""
        return result

    def stmt_while(self, result: Result) -> Result:
        """<stmt> -> <whileStmt>"""
        return result

    def stmt_expr(self, result: Result) -> Result:
        """<stmt> -> <expr> ';'"""
        return result

    def stmt_if(self, result: Result) -> Result:
        """<stmt> -> <ifStmt>"""
        return result

    def stmt_bloco(self, result: Result) -> Result:
        """<stmt> -> <bloco>"""
        return result

    def stmt_break(self, result: Result) -> Result:
        """<stmt> -> 'break' ';'"""
        break_label = self._loop_stack[-1].break_
        code = [Instruction.jump(break_label)]
        result.code.append((code, None))
        return result

    def stmt_continue(self, result: Result) -> Result:
        """<stmt> -> 'continue' ';'"""
        continue_label = self._loop_stack[-1].continue_
        code = [Instruction.jump(continue_label)]
        result.code.append((code, None))
        return result

    def stmt_return(self, result: Result) -> Result:
        """<stmt> -> 'return' <fator> ';'"""
        code = [Instruction.jump(self._return_label)]
        result.code.append((code, None))
        return result

    def stmt_declaration(self, result: Result) -> Result:
        """<stmt> -> <declaration>"""
        result.code.append(([], None))
        return result

    def stmt_null(self, result: Result) -> Result:
        """<stmt> -> ';'"""
        result.code.append(([], None))
        return result

    def declaration(self, result: Result) -> Result:
        """<declaration> -> <type> <identList> ';'"""
        return result

    def ident_list(self, result: Result) -> Result:
        """<identList> -> 'IDENT' <restoIdentList>"""
        return result

    def resto_ident_list(self, result: Result) -> Result:
        """<restoIdentList> -> ',' 'IDENT' <restoIdentList>"""
        return result

    def resto_ident_list_empty(self, result: Result) -> Result:
        """<restoIdentList> -> &"""
        return result

    def for_stmt_pre(self):
        """Called before for_stmt."""
        self._loop_stack.append(LoopLabels(self._generate_label(),
                                           self._generate_label()))

    def for_stmt(self, result: Result) -> Result:
        """<forStmt> -> 'for' '(' <optExpr> ';' <optExpr> ';'
                         <optExpr> ')' <stmt>
        """
        stmt_code, _ = result.code.pop()
        incr_code, _ = result.code.pop()
        cond_code, cond_value = result.code.pop()
        init_code, _ = result.code.pop()
        before, inside = (self._generate_label() for _ in range(2))
        after, incr = self._loop_stack.pop()
        code = init_code
        code.append(Instruction.label(before))
        code.extend(cond_code)
        code.append(Instruction.if_(cond_value, inside, after))
        code.append(Instruction.label(inside))
        code.extend(stmt_code)
        code.append(Instruction.label(incr))
        code.extend(incr_code)
        code.append(Instruction.jump(before))
        code.append(Instruction.label(after))
        result.code.append((code, None))
        return result

    def opt_expr(self, result: Result) -> Result:
        """<optExpr> -> <expr>"""
        return result

    def opt_expr_empty(self, result: Result) -> Result:
        """<optExpr> -> &"""
        result.code.append(([], 1))
        return result

    def io_stmt_scan(self, result: Result) -> Result:
        """<ioStmt> -> 'scan' '(' 'STR' ',' 'IDENT' ')' ';'"""
        ident = '__{1}__{0}'.format(*result.value.pop())
        command = f'scan_{result.type_.value}'
        code = [Instruction.call(command, result.value.pop(), ident)]
        result.code.append((code, None))
        return result

    def io_stmt_print(self, result: Result) -> Result:
        """<ioStmt> -> 'print' '(' <outList> ')' ';'"""
        return result

    def _out_list(self, result: Result) -> Result:
        resto_code = result.code.pop()[0]
        value = result.value.pop()
        if isinstance(value, tuple):
            value = '__{1}__{0}'.format(*value)
        code = [Instruction.call('print', value)]
        code.extend(resto_code)
        result.code.append((code, None))
        return result

    def out_list(self, result: Result) -> Result:
        """<outList> -> <out> <restoOutList>"""
        return self._out_list(result)

    def out(self, result: Result) -> Result:
        """<out> -> 'STR' | 'IDENT' | 'NUMint' | 'NUMfloat'"""
        return result

    def resto_out_list(self, result: Result) -> Result:
        """<restoOutList> -> ',' <out> <restoOutList>"""
        return self._out_list(result)

    def resto_out_list_empty(self, result: Result) -> Result:
        """<restoOutList> -> &"""
        result.code.append(([], None))
        return result

    def while_stmt_pre(self):
        """Called before while_stmt."""
        self._loop_stack.append(LoopLabels(self._generate_label(),
                                           self._generate_label()))

    def while_stmt(self, result: Result) -> Result:
        """<whileStmt> -> 'while' '(' <expr> ')' <stmt>"""
        stmt_code, _ = result.code.pop()
        expr_code, expr_value = result.code.pop()
        after, before = self._loop_stack.pop()
        inside = self._generate_label()
        code = [Instruction.label(before)]
        code.extend(expr_code)
        code.append(Instruction.if_(expr_value, inside, after))
        code.append(Instruction.label(inside))
        code.extend(stmt_code)
        code.append(Instruction.jump(before))
        code.append(Instruction.label(after))
        result.code.append((code, None))
        return result

    def if_stmt(self, result: Result) -> Result:
        """<ifStmt> -> 'if' '(' <expr> ')' <stmt> <elsePart>"""
        else_code, else_label = result.code.pop()
        stmt_code, _ = result.code.pop()
        expr_code, expr_value = result.code.pop()
        if_label = self._generate_label()
        code = expr_code
        code.append(Instruction.if_(expr_value, if_label, else_label))
        code.append(Instruction.label(if_label))
        code.extend(stmt_code)
        code.extend(else_code)
        result.code.append((code, None))
        return result

    def else_part(self, result: Result) -> Result:
        """<elsePart> -> 'else' <stmt>"""
        label = self._generate_label()
        code = [Instruction.label(label)]
        stmt_code = result.code.pop()[0]
        code.extend(stmt_code)
        result.code.append((code, label))
        return result

    def else_part_empty(self, result: Result) -> Result:
        """<elsePart> -> &"""
        label = self._generate_label()
        result.code.append(([Instruction.label(label)], label))
        return result

    def expr(self, result: Result) -> Result:
        """<expr> -> <atrib>"""
        return result

    def atrib(self, result: Result) -> Result:
        """<atrib> -> <or> <restoAtrib>"""
        resto_code, resto_value = result.code.pop()
        if resto_value is not None:
            code, value = result.code.pop()
            code.extend(resto_code)
            code.append(Instruction.operation('+', 0, resto_value, value))
            result.code.append((code, value))
        return result

    def resto_atrib(self, result: Result) -> Result:
        """<restoAtrib> -> '=' <atrib>"""
        return result

    def resto_atrib_empty(self, result: Result) -> Result:
        """<restoAtrib> -> &"""
        result.code.append(([], None))
        return result

    def or_(self, result: Result) -> Result:
        """<or> -> <and> <restoOr>"""
        return self._oper(result, resto=False)

    def resto_or(self, result: Result) -> Result:
        """<restoOr> -> '||' <and> <restoOr>"""
        return self._oper(result, '||', resto=True)

    def resto_or_empty(self, result: Result) -> Result:
        """<restoOr> -> &"""
        return self._empty(result)

    def and_(self, result: Result) -> Result:
        """<and> -> <not> <restoAnd>"""
        return self._oper(result, resto=False)

    def resto_and(self, result: Result) -> Result:
        """<restoAnd> -> '&&' <not> <restoAnd>"""
        return self._oper(result, '&&', resto=True)

    def resto_and_empty(self, result: Result) -> Result:
        """<restoAnd> -> &"""
        return self._empty(result)

    def not_not(self, result: Result) -> Result:
        """<not> -> '!' <not>"""
        code, value = result.code.pop()
        temp = self._generate_temp()
        code.append(Instruction.unary('!', value, temp))
        result.code.append((code, temp))
        return result

    def not_rel(self, result: Result) -> Result:
        """<not> -> <rel>"""
        return result

    def rel(self, result: Result) -> Result:
        """<rel> -> <add> <restoRel>"""
        return self._oper(result, resto=False)

    def resto_rel_eq(self, result: Result) -> Result:
        """<restoRel> -> '==' <add>"""
        result = self._empty(result)
        return self._oper(result, '==', resto=True)

    def resto_rel_neq(self, result: Result) -> Result:
        """<restoRel> -> '!=' <add>"""
        result = self._empty(result)
        return self._oper(result, '!=', resto=True)

    def resto_rel_gt(self, result: Result) -> Result:
        """<restoRel> -> '>' <add>"""
        result = self._empty(result)
        return self._oper(result, '>', resto=True)

    def resto_rel_geq(self, result: Result) -> Result:
        """<restoRel> -> '>=' <add>"""
        result = self._empty(result)
        return self._oper(result, '>=', resto=True)

    def resto_rel_lt(self, result: Result) -> Result:
        """<restoRel> -> '<' <add>"""
        result = self._empty(result)
        return self._oper(result, '<', resto=True)

    def resto_rel_leq(self, result: Result) -> Result:
        """<restoRel> -> '<=' <add>"""
        result = self._empty(result)
        return self._oper(result, '<=', resto=True)

    def resto_rel_empty(self, result: Result) -> Result:
        """<restoRel> -> &"""
        return self._empty(result)

    def add(self, result: Result) -> Result:
        """<add> -> <mult> <restoAdd>"""
        return self._oper(result, resto=False)

    def resto_add_plus(self, result: Result) -> Result:
        """<restoAdd> -> '+' <mult> <restoAdd>"""
        return self._oper(result, '+', resto=True)

    def resto_add_minus(self, result: Result) -> Result:
        """<restoAdd> -> '-' <mult> <restoAdd>"""
        return self._oper(result, '-', resto=True)

    def resto_add_empty(self, result: Result) -> Result:
        """<restoAdd> -> &"""
        return self._empty(result)

    def mult(self, result: Result) -> Result:
        """<mult> -> <uno> <restoMult>"""
        return self._oper(result, resto=False)

    def resto_mult_mult(self, result: Result) -> Result:
        """<restoMult> -> '*' <uno> <restoMult>"""
        return self._oper(result, '*', resto=True)

    def resto_mult_div(self, result: Result) -> Result:
        """<restoMult> -> '/' <uno> <restoMult>"""
        return self._oper(result, '/', resto=True)

    def resto_mult_mod(self, result: Result) -> Result:
        """<restoMult> -> '%' <uno> <restoMult>"""
        return self._oper(result, '%', resto=True)

    def resto_mult_empty(self, result: Result) -> Result:
        """<restoMult> -> &"""
        return self._empty(result)

    def uno_plus(self, result: Result) -> Result:
        """<uno> -> '+' <uno>"""
        return result

    def uno_minus(self, result: Result) -> Result:
        """<uno> -> '-' <uno>"""
        code, value = result.code.pop()
        temp = self._generate_temp()
        code.append(Instruction.operation('-', 0, value, temp))
        result.code.append((code, temp))
        return result

    def uno_fator(self, result: Result) -> Result:
        """<uno> -> <fator>"""
        return result

    def fator_ident(self, result: Result) -> Result:
        """<fator> -> 'IDENT'"""
        result.code.append(([], '__{1}__{0}'.format(*result.value.pop())))
        return result

    def fator_num(self, result: Result) -> Result:
        """<fator> -> 'NUMint' | 'NUMfloat'"""
        result.code.append(([], result.value.pop()))
        return result

    def fator_atrib(self, result: Result) -> Result:
        """<fator> -> '(' <atrib> ')'"""
        return result

    def _oper(self, result: Result, operator: str = '+', *,
              resto: bool) -> Result:
        resto_code, resto_value = result.code.pop()
        code, value = result.code.pop()
        if resto:
            left = self._generate_temp()
            dest = left
            code.append(Instruction.operation(operator, left, value,
                                              resto_value))
        elif resto_code:
            dest = self._expression_result
            resto_code[0].change_arg(0, value)
        else:
            dest = value
        code.extend(resto_code)
        result.code.append((code, dest))
        return result

    def _empty(self, result: Result) -> Result:
        self._expression_result = self._generate_temp()
        result.code.append(([], self._expression_result))
        return result
