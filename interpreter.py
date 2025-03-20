from lexer import Token, TokenType
from parser import (
    Expr, Binary, Grouping, Literal, Unary, Variable, Assignment, Logical, Call,
    Stmt, Expression, Print, Var, Block, If, While, Function as FunctionStmt, Return
)

class Environment:
    def __init__(self, enclosing=None):
        self.values = {}
        self.enclosing = enclosing

    def define(self, name, value):
        self.values[name] = value

    def get(self, name):
        if name.lexeme in self.values:
            return self.values[name.lexeme]

        if self.enclosing:
            return self.enclosing.get(name)

        raise RuntimeError(f"Undefined variable '{name.lexeme}'.")

    def assign(self, name, value):
        if name.lexeme in self.values:
            self.values[name.lexeme] = value
            return

        if self.enclosing:
            self.enclosing.assign(name, value)
            return

        raise RuntimeError(f"Undefined variable '{name.lexeme}'.")

class ReturnException(Exception):
    def __init__(self, value):
        self.value = value

class Function:
    def __init__(self, declaration, closure):
        self.declaration = declaration
        self.closure = closure

    def call(self, interpreter, arguments):
        environment = Environment(self.closure)

        for i in range(len(self.declaration.params)):
            environment.define(self.declaration.params[i].lexeme, arguments[i])

        try:
            interpreter.execute_block(self.declaration.body, environment)
        except ReturnException as return_value:
            return return_value.value

        return None

    def arity(self):
        return len(self.declaration.params)

    def __str__(self):
        return f"<fn {self.declaration.name.lexeme}>"

class Interpreter:
    def __init__(self):
        self.globals = Environment()
        self.environment = self.globals

        # Define native functions
        self.globals.define("clock", Clock())

    def interpret(self, statements):
        try:
            for statement in statements:
                self.execute(statement)
        except Exception as error:
            print(f"Runtime Error: {error}")

    def execute(self, stmt):
        if isinstance(stmt, Expression):
            self.evaluate(stmt.expression)
        elif isinstance(stmt, Print):
            value = self.evaluate(stmt.expression)
            print(value)
        elif isinstance(stmt, Var):
            value = None
            if stmt.initializer:
                value = self.evaluate(stmt.initializer)

            self.environment.define(stmt.name.lexeme, value)
        elif isinstance(stmt, Block):
            self.execute_block(stmt.statements, Environment(self.environment))
        elif isinstance(stmt, If):
            if self.is_truthy(self.evaluate(stmt.condition)):
                self.execute(stmt.then_branch)
            elif stmt.else_branch:
                self.execute(stmt.else_branch)
        elif isinstance(stmt, While):
            while self.is_truthy(self.evaluate(stmt.condition)):
                self.execute(stmt.body)
        elif isinstance(stmt, FunctionStmt):
            function = Function(stmt, self.environment)
            self.environment.define(stmt.name.lexeme, function)
        elif isinstance(stmt, Return):
            value = None
            if stmt.value:
                value = self.evaluate(stmt.value)

            raise ReturnException(value)

    def execute_block(self, statements, environment):
        previous = self.environment
        try:
            self.environment = environment

            for statement in statements:
                self.execute(statement)
        finally:
            self.environment = previous

    def evaluate(self, expr):
        if isinstance(expr, Literal):
            return expr.value
        elif isinstance(expr, Grouping):
            return self.evaluate(expr.expression)
        elif isinstance(expr, Unary):
            right = self.evaluate(expr.right)

            if expr.operator.type == TokenType.MINUS:
                self.check_number_operand(expr.operator, right)
                return -float(right)
            elif expr.operator.type == TokenType.BANG:
                return not self.is_truthy(right)

            return None
        elif isinstance(expr, Binary):
            left = self.evaluate(expr.left)
            right = self.evaluate(expr.right)

            if expr.operator.type == TokenType.MINUS:
                self.check_number_operands(expr.operator, left, right)
                return float(left) - float(right)
            elif expr.operator.type == TokenType.SLASH:
                self.check_number_operands(expr.operator, left, right)
                return float(left) / float(right)
            elif expr.operator.type == TokenType.STAR:
                self.check_number_operands(expr.operator, left, right)
                return float(left) * float(right)
            elif expr.operator.type == TokenType.PLUS:
                if (isinstance(left, float) and isinstance(right, float)) or \
                   (isinstance(left, int) and isinstance(right, int)):
                    return float(left) + float(right)
                if (isinstance(left, str) and isinstance(right, str)):
                    return str(left) + str(right)

                raise RuntimeError("Operands must be two numbers or two strings.")
            elif expr.operator.type == TokenType.GREATER:
                self.check_number_operands(expr.operator, left, right)
                return float(left) > float(right)
            elif expr.operator.type == TokenType.GREATER_EQUAL:
                self.check_number_operands(expr.operator, left, right)
                return float(left) >= float(right)
            elif expr.operator.type == TokenType.LESS:
                self.check_number_operands(expr.operator, left, right)
                return float(left) < float(right)
            elif expr.operator.type == TokenType.LESS_EQUAL:
                self.check_number_operands(expr.operator, left, right)
                return float(left) <= float(right)
            elif expr.operator.type == TokenType.BANG_EQUAL:
                return not self.is_equal(left, right)
            elif expr.operator.type == TokenType.EQUAL_EQUAL:
                return self.is_equal(left, right)

            return None
        elif isinstance(expr, Variable):
            return self.environment.get(expr.name)
        elif isinstance(expr, Assignment):
            value = self.evaluate(expr.value)
            self.environment.assign(expr.name, value)
            return value
        elif isinstance(expr, Logical):
            left = self.evaluate(expr.left)

            if expr.operator.type == TokenType.OR:
                if self.is_truthy(left):
                    return left
            else:
                if not self.is_truthy(left):
                    return left

            return self.evaluate(expr.right)
        elif isinstance(expr, Call):
            callee = self.evaluate(expr.callee)

            arguments = []
            for argument in expr.arguments:
                arguments.append(self.evaluate(argument))

            if not hasattr(callee, 'call'):
                raise RuntimeError("Can only call functions and classes.")

            function = callee
            if len(arguments) != function.arity():
                raise RuntimeError(f"Expected {function.arity()} arguments but got {len(arguments)}.")

            return function.call(self, arguments)

    def is_truthy(self, value):
        if value is None:
            return False
        if isinstance(value, bool):
            return value
        return True

    def is_equal(self, a, b):
        if a is None and b is None:
            return True
        if a is None:
            return False

        return a == b

    def check_number_operand(self, operator, operand):
        if isinstance(operand, float) or isinstance(operand, int):
            return
        raise RuntimeError("Operand must be a number.")

    def check_number_operands(self, operator, left, right):
        if (isinstance(left, float) or isinstance(left, int)) and \
           (isinstance(right, float) or isinstance(right, int)):
            return
        raise RuntimeError("Operands must be numbers.")

class Clock:
    def call(self, interpreter, arguments):
        import time
        return time.time()

    def arity(self):
        return 0

    def __str__(self):
        return "<native fn>"