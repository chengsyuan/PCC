import utils

clausecounter = utils.ClauseCounter()


class UnaryOP:
    def __init__(self, op='~', factor=None):
        self.op = op
        self.factor = factor

    def _asm(self, reg='eax'):
        src = ""
        if self.op == '-':
            src += self.factor._asm()
            src += "neg %rax\n"

        elif self.op == '!':
            src += self.factor._asm()
            src += "cmpq $0,%rax\n"
            src += "movq $0,%rax\n"
            src += "sete %al\n"

        elif self.op == '~':
            src += self.factor._asm()
            src += "not %rax\n"

        elif self.op == '++':
            src += self.factor._asm()
            src += "inc %rax\n"
            src += "movq %rax,{}(%rbp)\n". \
                format(varMap[self.factor.id_name])

        elif self.op == '--':
            src += self.factor._asm()
            src += "dec %rax\n"
            src += "movq %rax,{}(%rbp)\n". \
                format(varMap[self.factor.id_name])

        else:
            print("unknown operator")
            exit(0)

        return src


class Number:
    # can handle only int now
    def __init__(self, num=0):
        self.num = int(num)

    def _asm(self):
        src = "movq ${},%rax\n".format(self.num)
        return src


class Factor:
    def __init__(self, expression=None):
        self.expression = expression

    def _asm(self, reg='eax'):
        return self.expression._asm()


class Term:
    def __init__(self, factor,
                 op=None, term=None):
        self.factor = factor
        self.term = term
        self.op = op

    def _asm(self, reg='eax'):
        if self.op is None:
            return self.factor._asm()

        src = ""
        if self.op == '*':
            src += self.factor._asm()
            src += "push %rax\n"
            src += self.term._asm()
            src += "pop %rcx\n"

            src += "imul %rcx\n"  # P545

        else:  # /
            src += self.factor._asm()
            src += "push %rax\n"
            src += self.term._asm()
            src += "cdq\n"

            src += "pop %rcx\n"
            src += "idiv %rcx\n"  # P542
        return src


class AdditiveExpression:
    def __init__(self, term,
                 op=None, expression=None):
        self.term = term
        self.expression = expression
        self.op = op

    def _asm(self, reg='eax'):
        if self.op is None:
            return self.term._asm()

        src = ""
        if self.op == '+':
            src += self.term._asm()
            src += "push %rax\n"
            src += self.expression._asm()
            src += "pop %rcx\n"

            src += "addq %rcx,%rax\n"

        else:  # -
            src += self.term._asm()
            src += "push %rax\n"
            src += self.expression._asm()
            src += "pop %rcx\n"

            src += "subq %rcx,%rax\n"
        return src


class LogicalOrExpression:
    def __init__(self, logical_and_expression,
                 op=None, expression=None):
        self.logical_and_expression = logical_and_expression
        self.expression = expression
        self.op = op

    def _asm(self, reg='rax'):
        if self.op is None:
            return self.logical_and_expression._asm()

        src = ""
        if self.op == '||':
            fail_clause = clausecounter.next()
            ok_clause = clausecounter.next()

            src += self.expression._asm()
            src += 'cmpq $0,%rax\n'
            src += 'je {}\n'.format(fail_clause)
            src += 'movq $1,%rax\n'
            src += 'jmp {}\n'.format(ok_clause)

            src += '{}:\n'.format(fail_clause)
            src += self.logical_and_expression._asm()
            src += 'cmpq $0,%rax\n'
            src += 'movq $1,%rax\n'
            src += "setne %al\n"

            src += '{}:\n'.format(ok_clause)

        return src


class LogicalAndExpression:
    def __init__(self, equality_expression,
                 op=None, logical_and_expression=None):
        self.equality_expression = equality_expression
        self.logical_and_expression = logical_and_expression
        self.op = op

    def _asm(self, reg='rax'):
        if self.op is None:
            return self.equality_expression._asm()

        src = ""
        if self.op == '&&':
            fail_clause = clausecounter.next()
            ok_clause = clausecounter.next()

            src += self.logical_and_expression._asm()
            src += 'cmpq $0,%rax\n'
            src += 'jne {}\n'.format(fail_clause)
            src += 'jmp {}\n'.format(ok_clause)

            src += '{}:\n'.format(fail_clause)
            src += self.equality_expression._asm()
            src += 'cmpq $0,%rax\n'
            src += 'movq $1,%rax\n'
            src += "setne %al\n"

            src += '{}:\n'.format(ok_clause)

        return src


class EqualityExpression:
    def __init__(self, relational_expression,
                 op=None, equality_expression=None):
        self.relational_expression = relational_expression
        self.equality_expression = equality_expression
        self.op = op

    def _asm(self, reg='rax'):
        if self.op is None:
            return self.relational_expression._asm()

        src = ""
        if self.op == '==':
            src += self.relational_expression._asm()
            src += "push %rax\n"

            src += self.equality_expression._asm()
            src += "pop %rcx\n"

            src += "cmpq %rcx,%rax\n"
            src += "movq $0,%rax\n"
            src += "sete %al\n"

        elif self.op == '!=':
            src += self.relational_expression._asm()
            src += "push %rax\n"

            src += self.equality_expression._asm()
            src += "pop %rcx\n"

            src += "cmpq %rcx,%rax\n"
            src += "movq $0,%rax\n"
            src += "setne %al\n"
        return src


class RelationalExpression:
    def __init__(self, additive_expression,
                 op=None, relational_expression=None):
        self.additive_expression = additive_expression
        self.relational_expression = relational_expression
        self.op = op

    def _asm(self, reg='rax'):
        if self.op is None:
            return self.additive_expression._asm()

        src = ""
        if self.op == '>':
            src += self.relational_expression._asm()
            src += "push %rax\n"

            src += self.additive_expression._asm()
            src += "pop %rcx\n"

            src += "cmpq %rcx,%rax\n"
            src += "movq $0,%rax\n"
            src += "setl %al\n"

        elif self.op == '<':
            src += self.relational_expression._asm()
            src += "push %rax\n"

            src += self.additive_expression._asm()
            src += "pop %rcx\n"

            src += "cmpq %rax,%rcx\n"
            src += "movq $0,%rax\n"
            src += "setl %al\n"

        elif self.op == '>=':
            src += self.relational_expression._asm()
            src += "push %rax\n"

            src += self.additive_expression._asm()
            src += "pop %rcx\n"

            src += "cmpq %rcx,%rax\n"
            src += "movq $0,%rax\n"
            src += "setle %al\n"

        elif self.op == '<=':
            src += self.relational_expression._asm()
            src += "push %rax\n"

            src += self.additive_expression._asm()
            src += "pop %rcx\n"

            src += "cmpq %rax,%rcx\n"
            src += "movq $0,%rax\n"
            src += "setle %al\n"
        return src


class Expression:
    def __init__(self, logical_or_expression,
                 f_name=None, expression=None):
        self.logical_or_expression = logical_or_expression
        self.f_name = f_name
        self.expression = expression

    def _asm(self, reg='rax'):
        if self.f_name is None:
            return self.logical_or_expression._asm()

        src = ""

        return src


varMap = {}
stack_index = -8


class Assignment:
    def __init__(self, id_name, expression, op):
        self.id_name = id_name
        self.expression = expression
        self.op = op

    def _asm(self):
        if self.id_name not in varMap:
            print('{} is not defined'.format(self.id_name))
            exit(0)
        src = ""

        if self.op == '=':
            src += self.expression._asm()
            src += "movq %rax,{}(%rbp)\n". \
                format(varMap[self.id_name])

        elif self.op == '+=':
            src += self.expression._asm()
            src += "addq %rax,{}(%rbp)\n". \
                format(varMap[self.id_name])

        elif self.op == '-=':
            src += self.expression._asm()
            src += "subq %rax,{}(%rbp)\n". \
                format(varMap[self.id_name])

        elif self.op == '*=':
            src += self.expression._asm()
            src += "movq {}(%rbp),%rcx\n". \
                format(varMap[self.id_name])
            src += "imul %rcx\n"

            src += "movq %rax,{}(%rbp)\n". \
                format(varMap[self.id_name])

        elif self.op == '/=':
            src += self.expression._asm()
            src += "movq %rax,%rcx\n"

            src += "movq {}(%rbp),%rax\n". \
                format(varMap[self.id_name])

            src += "cdq\n"
            src += "idiv %rcx\n"

            src += "movq %rax,{}(%rbp)\n". \
                format(varMap[self.id_name])

        elif self.op == '%=':
            src += self.expression._asm()
            src += "movq %rax,%rcx\n"

            src += "movq {}(%rbp),%rax\n". \
                format(varMap[self.id_name])

            src += "cdq\n"
            src += "idiv %rcx\n"

            src += "movq %rdx,{}(%rbp)\n". \
                format(varMap[self.id_name])

        elif self.op == '<<=':
            src += self.expression._asm()
            src += "movq %rax,%rcx\n"

            src += "movq {}(%rbp),%rax\n". \
                format(varMap[self.id_name])

            src += "shll %cl,%eax\n"

            src += "movq %rax,{}(%rbp)\n". \
                format(varMap[self.id_name])

        elif self.op == '>>=':
            src += self.expression._asm()
            src += "movq %rax,%rcx\n"

            src += "movq {}(%rbp),%rax\n". \
                format(varMap[self.id_name])

            src += "shrl %cl,%eax\n"

            src += "movq %rax,{}(%rbp)\n". \
                format(varMap[self.id_name])

        elif self.op == '&=':  # P61
            src += self.expression._asm()
            src += "push %rax\n"

            src += "movq {}(%rbp),%rax\n". \
                format(varMap[self.id_name])

            src += "pop %rcx\n"
            src += "and %rcx,%rax\n"

            src += "movq %rax,{}(%rbp)\n". \
                format(varMap[self.id_name])

        elif self.op == '^=':
            src += self.expression._asm()
            src += "push %rax\n"

            src += "movq {}(%rbp),%rax\n". \
                format(varMap[self.id_name])

            src += "pop %rcx\n"
            src += "xor %rcx,%rax\n"

            src += "movq %rax,{}(%rbp)\n". \
                format(varMap[self.id_name])

        elif self.op == '|=':
            src += self.expression._asm()
            src += "push %rax\n"

            src += "movq {}(%rbp),%rax\n". \
                format(varMap[self.id_name])

            src += "pop %rcx\n"
            src += "or %rcx,%rax\n"

            src += "movq %rax,{}(%rbp)\n". \
                format(varMap[self.id_name])

        elif self.op == ',':
            src += self.expression._asm()

        else:
            print("unknown operator")
            exit(0)

        return src


class Declaration:
    def __init__(self, type_name, id_name, expression=None):
        self.type_name = type_name
        self.id_name = id_name
        self.expression = expression

    def _asm(self):
        if self.id_name in varMap:
            print('{} is already defined'.format(self.id_name))
            exit(0)

        src = ""

        # default value is zero!
        if self.expression is None:
            src += "movq $0,%rax\n"
        else:
            src += self.expression._asm()

        src += "push %rax\n"

        global stack_index
        varMap[self.id_name] = stack_index
        stack_index -= 8

        return src


class Variable:
    def __init__(self, id_name):
        self.id_name = id_name

    def _asm(self):
        if self.id_name not in varMap:
            print('{} is not defined'.format(self.id_name))
            exit(0)

        src = ""
        src += "movq {}(%rbp),%rax\n". \
            format(varMap[self.id_name])

        return src


class Return:
    def __init__(self, expression=None):
        self.expression = expression

    def _asm(self):
        src = ""
        src += self.expression._asm()
        for _ in range(len(varMap.keys())):
            src += "popq %rbp\n"
        src += "popq %rbp\n"
        src += "ret\n"
        return src


class Condition:
    def __init__(self, condition_expression, if_statement, else_statement=None):
        self.condition_expression = condition_expression
        self.if_statement = if_statement
        self.else_statement = else_statement

    def _asm(self, reg='rax'):
        src = ""

        # if_clause = clausecounter.next()
        else_clause = clausecounter.next()
        end_clause = clausecounter.next()

        src += self.condition_expression._asm()
        src += 'cmpq $0,%rax\n'
        src += 'je {}\n'.format(else_clause)
        src += self.if_statement._asm()
        src += 'jmp {}\n'.format(end_clause)

        src += '{}:\n'.format(else_clause)

        if self.else_statement is not None:
            src += self.else_statement._asm()

        src += '{}:\n'.format(end_clause)

        return src

class Function:
    def __init__(self, fname, rtype, statement, function=None):
        self.rtype = rtype
        self.fname = fname
        self.statement = statement
        self.function = function

    def _asm(self, header=True):
        """
        one line code also needs a header
        :param header:
        :return:
        """
        if self.function is None:
            if header:
                return self._header() + self.statement._asm()
            else:
                return self.statement._asm()

        src = ""

        if header:
            src = self._header()

        # add former lines
        src += self.function._asm(header=False)
        # add this line
        src += self.statement._asm()
        return src

    def _header(self):
        src = ""
        src += '.globl _{}\n'.format(self.fname)
        src += '_{}:\n'.format(self.fname)
        src += 'pushq %rbp\n'
        src += 'movq %rsp,%rbp\n'
        return src


class Program:
    def __init__(self, function=None):
        self.function = function

    def __str__(self):
        return self.function._asm()