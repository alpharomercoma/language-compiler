from typing import List, Dict, Any, Optional
from parser import (
    Expr, Binary, Grouping, Literal, Unary, Variable, Assignment, Logical, Call,
    Stmt, Expression, Print, Var, Block, If, While, Function as FunctionStmt, Return
)

class IRInstruction:
    def __init__(self, opcode: str, operands: List[Any] = None) -> None:
        self.opcode = opcode
        self.operands = operands or []

class IRGenerator:
    def __init__(self) -> None:
        self.instructions: List[IRInstruction] = []
        self.current_function: Optional[str] = None
        self.label_counter: int = 0

    def generate(self, statements: List[Stmt]) -> List[IRInstruction]:
        self.instructions = []
        for stmt in statements:
            self.visit_statement(stmt)
        return self.instructions

    def visit_statement(self, stmt: Stmt) -> None:
        if isinstance(stmt, Expression):
            self.visit_expression(stmt.expression)
        elif isinstance(stmt, Print):
            self.visit_expression(stmt.expression)
            self.instructions.append(IRInstruction("PRINT"))
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

    def visit_expression(self, expr: Expr) -> None:
        if isinstance(expr, Binary):
            self.visit_binary(expr)
        elif isinstance(expr, Grouping):
            self.visit_expression(expr.expression)
        elif isinstance(expr, Literal):
            self.visit_literal(expr)
        elif isinstance(expr, Unary):
            self.visit_unary(expr)
        elif isinstance(expr, Variable):
            self.visit_variable(expr)
        elif isinstance(expr, Assignment):
            self.visit_assignment(expr)
        elif isinstance(expr, Logical):
            self.visit_logical(expr)
        elif isinstance(expr, Call):
            self.visit_call(expr)

    def visit_binary(self, expr: Binary) -> None:
        self.visit_expression(expr.left)
        self.visit_expression(expr.right)

        if expr.operator.type == "PLUS":
            self.instructions.append(IRInstruction("ADD"))
        elif expr.operator.type == "MINUS":
            self.instructions.append(IRInstruction("SUB"))
        elif expr.operator.type == "STAR":
            self.instructions.append(IRInstruction("MUL"))
        elif expr.operator.type == "SLASH":
            self.instructions.append(IRInstruction("DIV"))

    def visit_literal(self, expr: Literal) -> None:
        self.instructions.append(IRInstruction("CONST", [expr.value]))

    def visit_variable(self, expr: Variable) -> None:
        self.instructions.append(IRInstruction("LOAD", [expr.name.lexeme]))

    def visit_assignment(self, expr: Assignment) -> None:
        self.visit_expression(expr.value)
        self.instructions.append(IRInstruction("STORE", [expr.name.lexeme]))

    def visit_call(self, expr: Call) -> None:
        for arg in expr.arguments:
            self.visit_expression(arg)
        self.instructions.append(IRInstruction("CALL", [expr.callee.name.lexeme]))

    def visit_var_declaration(self, stmt: Var) -> None:
        if stmt.initializer:
            self.visit_expression(stmt.initializer)
        else:
            self.instructions.append(IRInstruction("CONST", [0]))  # Default value
        self.instructions.append(IRInstruction("STORE", [stmt.name.lexeme]))

    def visit_block(self, stmt: Block) -> None:
        for statement in stmt.statements:
            self.visit_statement(statement)

    def visit_function_declaration(self, stmt: FunctionStmt) -> None:
        self.current_function = stmt.name.lexeme
        self.instructions.append(IRInstruction("FUNC", [stmt.name.lexeme]))

        # Add parameters to function scope
        for param in stmt.params:
            self.instructions.append(IRInstruction("PARAM", [param.lexeme]))

        # Generate function body
        for stmt in stmt.body:
            self.visit_statement(stmt)

        self.instructions.append(IRInstruction("RETURN"))
        self.current_function = None

    def visit_if_statement(self, stmt: If) -> None:
        self.visit_expression(stmt.condition)
        else_label = self.new_label()
        end_label = self.new_label()

        self.instructions.append(IRInstruction("JMP_FALSE", [else_label]))
        self.visit_statement(stmt.then_branch)
        self.instructions.append(IRInstruction("JMP", [end_label]))

        self.instructions.append(IRInstruction("LABEL", [else_label]))
        if stmt.else_branch:
            self.visit_statement(stmt.else_branch)

        self.instructions.append(IRInstruction("LABEL", [end_label]))

    def visit_while_statement(self, stmt: While) -> None:
        start_label = self.new_label()
        end_label = self.new_label()

        self.instructions.append(IRInstruction("LABEL", [start_label]))
        self.visit_expression(stmt.condition)
        self.instructions.append(IRInstruction("JMP_FALSE", [end_label]))

        self.visit_statement(stmt.body)
        self.instructions.append(IRInstruction("JMP", [start_label]))
        self.instructions.append(IRInstruction("LABEL", [end_label]))

    def visit_return_statement(self, stmt: Return) -> None:
        if stmt.value:
            self.visit_expression(stmt.value)
        else:
            self.instructions.append(IRInstruction("CONST", [None]))
        self.instructions.append(IRInstruction("RETURN"))

    def visit_unary(self, expr: Unary) -> None:
        self.visit_expression(expr.right)
        if expr.operator.type == "MINUS":
            self.instructions.append(IRInstruction("NEG"))
        elif expr.operator.type == "BANG":
            self.instructions.append(IRInstruction("NOT"))

    def visit_logical(self, expr: Logical) -> None:
        self.visit_expression(expr.left)
        self.visit_expression(expr.right)
        if expr.operator.type == "OR":
            self.instructions.append(IRInstruction("OR"))
        elif expr.operator.type == "AND":
            self.instructions.append(IRInstruction("AND"))

    def new_label(self) -> str:
        self.label_counter += 1
        return f"L{self.label_counter}"