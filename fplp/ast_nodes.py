"""FPLP Language - AST Node Definitions"""


class Node:
    """Base AST node."""
    def token_literal(self):
        raise NotImplementedError

    def __repr__(self):
        return self.__str__()


class Statement(Node):
    """Base statement node."""
    pass


class Expression(Node):
    """Base expression node."""
    pass


class Program(Statement):
    """Root node - list of statements."""
    def __init__(self, statements=None):
        self.statements = statements or []

    def __str__(self):
        return '\n'.join(str(s) for s in self.statements)

    def token_literal(self):
        return "program"


class LetStatement(Statement):
    """let identifier = expression"""
    def __init__(self, name, value):
        self.name = name       # Identifier
        self.value = value     # Expression

    def __str__(self):
        return f"(let {self.name} = {self.value})"

    def token_literal(self):
        return "let"


class ReturnStatement(Statement):
    """return expression"""
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return f"(return {self.value})"

    def token_literal(self):
        return "return"


class ExpressionStatement(Statement):
    """A standalone expression used as a statement."""
    def __init__(self, expression):
        self.expression = expression

    def __str__(self):
        return str(self.expression) if self.expression else ""

    def token_literal(self):
        return str(self.expression) if self.expression else ""


class BlockStatement(Statement):
    """{ statements }"""
    def __init__(self, statements=None):
        self.statements = statements or []

    def __str__(self):
        return '{ ' + '; '.join(str(s) for s in self.statements) + ' }'

    def token_literal(self):
        return "block"


class AssignStatement(Statement):
    """identifier = expression (re-assignment)"""
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def __str__(self):
        return f"({self.name} = {self.value})"

    def token_literal(self):
        return "="


# --- Expressions ---

class Identifier(Expression):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return self.value

    def token_literal(self):
        return self.value


class NumberLiteral(Expression):
    def __init__(self, value):
        self.value = value  # int or float

    def __str__(self):
        if isinstance(self.value, float):
            return str(self.value)
        return str(self.value)

    def token_literal(self):
        return str(self.value)


class StringLiteral(Expression):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return '"' + self.value + '"'

    def token_literal(self):
        return self.value


class BooleanLiteral(Expression):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return "true" if self.value else "false"

    def token_literal(self):
        return "true" if self.value else "false"


class NilLiteral(Expression):
    def __str__(self):
        return "nil"

    def token_literal(self):
        return "nil"


class ArrayLiteral(Expression):
    def __init__(self, elements):
        self.elements = elements or []

    def __str__(self):
        return '[' + ', '.join(str(e) for e in self.elements) + ']'

    def token_literal(self):
        return "array"


class MapLiteral(Expression):
    def __init__(self, pairs):
        self.pairs = pairs or {}  # dict of {Expression: Expression}

    def __str__(self):
        items = ', '.join(f'{k}: {v}' for k, v in self.pairs.items())
        return '{' + items + '}'

    def token_literal(self):
        return "map"


class PrefixExpression(Expression):
    def __init__(self, operator, right):
        self.operator = operator
        self.right = right

    def __str__(self):
        return f'({self.operator}{self.right})'

    def token_literal(self):
        return self.operator


class InfixExpression(Expression):
    def __init__(self, left, operator, right):
        self.left = left
        self.operator = operator
        self.right = right

    def __str__(self):
        return f'({self.left} {self.operator} {self.right})'

    def token_literal(self):
        return self.operator


class IfExpression(Expression):
    def __init__(self, condition, consequence, alternative=None):
        self.condition = condition
        self.consequence = consequence    # BlockStatement
        self.alternative = alternative    # BlockStatement or None

    def __str__(self):
        s = f'(if {self.condition} {self.consequence}'
        if self.alternative:
            s += f' else {self.alternative}'
        return s + ')'

    def token_literal(self):
        return "if"


class LoopExpression(Statement):
    """
    loop identifier in iterable { body }
    loop condition { body }
    """
    def __init__(self, identifier, iterable, body, is_while=False):
        self.identifier = identifier  # Identifier or None (while form)
        self.iterable = iterable      # Expression or None (while condition)
        self.body = body              # BlockStatement
        self.is_while = is_while

    def __str__(self):
        if self.is_while:
            return f'(loop {self.iterable} {self.body})'
        return f'(loop {self.identifier} in {self.iterable} {self.body})'

    def token_literal(self):
        return "loop"


class FnLiteral(Expression):
    def __init__(self, parameters, body):
        self.parameters = parameters or []  # list of Identifier
        self.body = body                    # BlockStatement

    def __str__(self):
        params = ', '.join(str(p) for p in self.parameters)
        return f'(fn ({params}) {self.body})'

    def token_literal(self):
        return "fn"


class CallExpression(Expression):
    def __init__(self, function, arguments):
        self.function = function      # Expression (identifier or fn literal)
        self.arguments = arguments or []  # list of Expression

    def __str__(self):
        args = ', '.join(str(a) for a in self.arguments)
        return f'({self.function}({args}))'

    def token_literal(self):
        return "call"


class IndexExpression(Expression):
    def __init__(self, left, index):
        self.left = left
        self.index = index

    def __str__(self):
        return f'({self.left}[{self.index}])'

    def token_literal(self):
        return "index"
