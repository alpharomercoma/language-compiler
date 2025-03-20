from typing import Dict, List, Any, Optional
from lexer import Token, TokenType
from parser import (
    Expr, Binary, Grouping, Literal, Unary, Variable, Assignment, Logical, Call,
    Stmt, Expression, Print, Var, Block, If, While, Function as FunctionStmt, Return
)

class SemanticError(Exception):
    def __init__(self, token: Token, message: str) -> None:
        self.token = token
        self.message = message
        super().__init__(message)

class SemanticAnalyzer:
    def __init__(self) -> None:
        self.scopes: List[Dict[str, Optional[str]]] = [{}]  # Stack of scopes, each scope is a dict of variable names to their types
        self.current_scope: int = 0
        self.functions: Dict[str, List[str]] = {}  # Store function signatures
        # Register built-in functions
        self.register_native_functions()

    def register_native_functions(self) -> None:
        # In a full implementation, we would register native functions here
        pass

    def analyze(self, statements: List[Stmt]) -> bool:
        try:
            # First pass: register all function declarations
            for statement in statements:
                if isinstance(statement, FunctionStmt):
                    self.register_function(statement)

            # Second pass: analyze all statements
            for statement in statements:
                self.visit_statement(statement)
            return True
        except SemanticError as e:
            print(f"Semantic Error at line {e.token.line}: {e.message}")
            return False

    def register_function(self, stmt: FunctionStmt) -> None:
        # Register the function in the global scope
        self.functions[stmt.name.lexeme] = ["number"] * len(stmt.params)  # All params are numbers for simplicity
        # Store the function name in the current scope
        self.scopes[0][stmt.name.lexeme] = "function"

    def visit_statement(self, stmt: Stmt) -> None:
        if isinstance(stmt, Expression):
            self.visit_expression(stmt.expression)
        elif isinstance(stmt, Print):
            self.visit_expression(stmt.expression)
        elif isinstance(stmt, Var):
            self.visit_var_declaration(stmt)
        elif isinstance(stmt, Block):
            self.visit_block(stmt)
        elif isinstance(stmt, If):
            self.visit_if_statement(stmt)
        elif isinstance(stmt, While):
            self.visit_while_statement(stmt)
        elif isinstance(stmt, FunctionStmt):
            self.visit_function_declaration(stmt)
        elif isinstance(stmt, Return):
            self.visit_return_statement(stmt)

    def visit_expression(self, expr: Expr) -> str:
        if isinstance(expr, Binary):
            return self.visit_binary(expr)
        elif isinstance(expr, Grouping):
            return self.visit_expression(expr.expression)
        elif isinstance(expr, Literal):
            return self.visit_literal(expr)
        elif isinstance(expr, Unary):
            return self.visit_unary(expr)
        elif isinstance(expr, Variable):
            return self.visit_variable(expr)
        elif isinstance(expr, Assignment):
            return self.visit_assignment(expr)
        elif isinstance(expr, Logical):
            return self.visit_logical(expr)
        elif isinstance(expr, Call):
            return self.visit_call(expr)
        else:
            # Handle other expression types or raise an error
            return "unknown"

    def visit_binary(self, expr: Binary) -> str:
        left_type = self.visit_expression(expr.left)
        right_type = self.visit_expression(expr.right)

        # Type checking for arithmetic operations
        if expr.operator.type in [TokenType.PLUS, TokenType.MINUS, TokenType.STAR, TokenType.SLASH]:
            if not (self.is_numeric_type(left_type) and self.is_numeric_type(right_type)):
                raise SemanticError(expr.operator, "Operands must be numbers")
            return "number"

        # Type checking for comparison operations
        elif expr.operator.type in [TokenType.GREATER, TokenType.GREATER_EQUAL,
                                  TokenType.LESS, TokenType.LESS_EQUAL]:
            if not (self.is_numeric_type(left_type) and self.is_numeric_type(right_type)):
                raise SemanticError(expr.operator, "Operands must be numbers")
            return "boolean"

        # Type checking for equality operations
        elif expr.operator.type in [TokenType.BANG_EQUAL, TokenType.EQUAL_EQUAL]:
            if left_type != right_type and left_type != "unknown" and right_type != "unknown":
                raise SemanticError(expr.operator, "Operands must be of the same type")
            return "boolean"
        else:
            return "unknown"

    def visit_unary(self, expr: Unary) -> str:
        right_type = self.visit_expression(expr.right)

        if expr.operator.type == TokenType.MINUS:
            if not self.is_numeric_type(right_type):
                raise SemanticError(expr.operator, "Operand must be a number")
            return "number"
        elif expr.operator.type == TokenType.BANG:
            return "boolean"
        else:
            return "unknown"

    def visit_literal(self, expr: Literal) -> str:
        if isinstance(expr.value, bool):
            return "boolean"
        elif isinstance(expr.value, float):
            return "number"
        elif isinstance(expr.value, str):
            return "string"
        elif expr.value is None:
            return "nil"
        else:
            return "unknown"

    def visit_variable(self, expr: Variable) -> str:
        var_type = self.resolve_variable(expr.name)
        if var_type is None:
            raise SemanticError(expr.name, "Undefined variable")
        return var_type

    def visit_assignment(self, expr: Assignment) -> str:
        var_type = self.resolve_variable(expr.name)
        if var_type is None:
            raise SemanticError(expr.name, "Undefined variable")

        value_type = self.visit_expression(expr.value)
        if var_type != value_type and var_type != "unknown" and value_type != "unknown":
            raise SemanticError(expr.name, f"Cannot assign value of type {value_type} to variable of type {var_type}")

        return var_type

    def visit_logical(self, expr: Logical) -> str:
        left_type = self.visit_expression(expr.left)
        right_type = self.visit_expression(expr.right)

        if not (self.is_boolean_type(left_type) and self.is_boolean_type(right_type)):
            raise SemanticError(expr.operator, "Operands must be boolean")
        return "boolean"

    def visit_call(self, expr: Call) -> str:
        # Check if callee is a variable reference
        if not isinstance(expr.callee, Variable):
            raise SemanticError(expr.paren, "Can only call functions")

        # Get function name
        func_name = expr.callee.name.lexeme

        # Check if function exists
        if func_name not in self.functions:
            raise SemanticError(expr.paren, f"Undefined function '{func_name}'")

        # Check parameter count
        expected_params = self.functions[func_name]
        if len(expected_params) != len(expr.arguments):
            raise SemanticError(expr.paren,
                f"Expected {len(expected_params)} arguments but got {len(expr.arguments)}")

        # Check parameter types
        for i, arg in enumerate(expr.arguments):
            arg_type = self.visit_expression(arg)
            expected_type = expected_params[i]
            if arg_type != expected_type and arg_type != "unknown" and expected_type != "unknown":
                raise SemanticError(expr.paren,
                    f"Argument {i+1} expected type {expected_type} but got {arg_type}")

        return "number"  # Default return type for our simple language

    def visit_var_declaration(self, stmt: Var) -> None:
        var_type = "number"  # Default type for variables in our simple language
        if stmt.initializer:
            var_type = self.visit_expression(stmt.initializer)

        # Store variable type in current scope
        self.scopes[self.current_scope][stmt.name.lexeme] = var_type

    def visit_block(self, stmt: Block) -> None:
        self.begin_scope()
        for statement in stmt.statements:
            self.visit_statement(statement)
        self.end_scope()

    def visit_if_statement(self, stmt: If) -> None:
        condition_type = self.visit_expression(stmt.condition)
        if not self.is_boolean_type(condition_type) and condition_type != "unknown":
            raise SemanticError(stmt.condition, "Condition must be boolean")

        self.visit_statement(stmt.then_branch)
        if stmt.else_branch:
            self.visit_statement(stmt.else_branch)

    def visit_while_statement(self, stmt: While) -> None:
        condition_type = self.visit_expression(stmt.condition)
        if not self.is_boolean_type(condition_type) and condition_type != "unknown":
            raise SemanticError(stmt.condition, "Condition must be boolean")

        self.visit_statement(stmt.body)

    def visit_function_declaration(self, stmt: FunctionStmt) -> None:
        # Function signature already registered in first pass

        # Analyze function body in its own scope
        self.begin_scope()

        # Add parameters to function scope
        for param in stmt.params:
            self.scopes[self.current_scope][param.lexeme] = "number"

        # Analyze function body
        for statement in stmt.body:
            self.visit_statement(statement)

        self.end_scope()

    def visit_return_statement(self, stmt: Return) -> None:
        if stmt.value:
            return_type = self.visit_expression(stmt.value)
            if not self.is_numeric_type(return_type) and return_type != "unknown":
                raise SemanticError(stmt.keyword, "Return value must be a number")

    def begin_scope(self) -> None:
        self.scopes.append({})
        self.current_scope += 1

    def end_scope(self) -> None:
        self.scopes.pop()
        self.current_scope -= 1

    def resolve_variable(self, name: Token) -> Optional[str]:
        for i in range(self.current_scope, -1, -1):
            if name.lexeme in self.scopes[i]:
                return self.scopes[i][name.lexeme]
        return None

    def is_numeric_type(self, type_str: str) -> bool:
        return type_str == "number" or type_str == "unknown"

    def is_boolean_type(self, type_str: str) -> bool:
        return type_str == "boolean" or type_str == "unknown"