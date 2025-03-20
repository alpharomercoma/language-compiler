from typing import List, Dict, Any, Optional
from parser import (
    Expr, Binary, Grouping, Literal, Unary, Variable, Assignment, Logical, Call,
    Stmt, Expression, Print, Var, Block, If, While, Function as FunctionStmt, Return
)

class IRInstruction:
    def __init__(self, opcode: str, operands: List[Any] = None) -> None:
        self.opcode = opcode
        self.operands = operands or []

    def __str__(self) -> str:
        if not self.operands:
            return f"{self.opcode}"
        return f"{self.opcode} {', '.join(str(op) for op in self.operands)}"

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
            # Discard the result since expression statements don't use the value
            self.instructions.append(IRInstruction("POP"))
        elif isinstance(stmt, Print):
            self.visit_expression(stmt.expression)
            self.instructions.append(IRInstruction("PRINT"))
        elif isinstance(stmt, Var):
            if stmt.initializer is not None:
                self.visit_expression(stmt.initializer)
            else:
                # Default initialization to 0
                self.instructions.append(IRInstruction("CONST", [0]))
            self.instructions.append(IRInstruction("STORE", [stmt.name.lexeme]))
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
        else:
            raise RuntimeError(f"Unsupported statement type: {type(stmt)}")

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
        else:
            raise RuntimeError(f"Unsupported expression type: {type(expr)}")

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
        elif expr.operator.type == "GREATER":
            self.instructions.append(IRInstruction("GREATER"))
        elif expr.operator.type == "GREATER_EQUAL":
            self.instructions.append(IRInstruction("GREATER_EQUAL"))
        elif expr.operator.type == "LESS":
            self.instructions.append(IRInstruction("LESS"))
        elif expr.operator.type == "LESS_EQUAL":
            self.instructions.append(IRInstruction("LESS_EQUAL"))
        elif expr.operator.type == "EQUAL_EQUAL":
            self.instructions.append(IRInstruction("EQUAL"))
        elif expr.operator.type == "BANG_EQUAL":
            self.instructions.append(IRInstruction("NOT_EQUAL"))
        else:
            raise RuntimeError(f"Unsupported binary operator: {expr.operator.type}")

    def visit_literal(self, expr: Literal) -> None:
        self.instructions.append(IRInstruction("CONST", [expr.value]))

    def visit_variable(self, expr: Variable) -> None:
        self.instructions.append(IRInstruction("LOAD", [expr.name.lexeme]))

    def visit_assignment(self, expr: Assignment) -> None:
        self.visit_expression(expr.value)
        # Duplicate the value on the stack because assignment is also an expression
        self.instructions.append(IRInstruction("DUP"))
        self.instructions.append(IRInstruction("STORE", [expr.name.lexeme]))

    def visit_call(self, expr: Call) -> None:
        # Push arguments in reverse order
        for arg in reversed(expr.arguments):
            self.visit_expression(arg)

        # Call the function
        if isinstance(expr.callee, Variable):
            self.instructions.append(IRInstruction("CALL", [expr.callee.name.lexeme, len(expr.arguments)]))
        else:
            raise RuntimeError("Can only call functions by name")

    def visit_block(self, stmt: Block) -> None:
        for statement in stmt.statements:
            self.visit_statement(statement)

    def visit_if_statement(self, stmt: If) -> None:
        else_label = self.new_label()
        end_label = self.new_label()

        # Generate condition code
        self.visit_expression(stmt.condition)
        self.instructions.append(IRInstruction("JMP_FALSE", [else_label]))

        # Generate then branch code
        self.visit_statement(stmt.then_branch)
        self.instructions.append(IRInstruction("JMP", [end_label]))

        # Mark else branch
        self.instructions.append(IRInstruction("LABEL", [else_label]))

        # Generate else branch code if it exists
        if stmt.else_branch:
            self.visit_statement(stmt.else_branch)

        # Mark end of if statement
        self.instructions.append(IRInstruction("LABEL", [end_label]))

    def visit_while_statement(self, stmt: While) -> None:
        start_label = self.new_label()
        end_label = self.new_label()

        # Mark start of loop
        self.instructions.append(IRInstruction("LABEL", [start_label]))

        # Generate condition code
        self.visit_expression(stmt.condition)
        self.instructions.append(IRInstruction("JMP_FALSE", [end_label]))

        # Generate loop body
        self.visit_statement(stmt.body)

        # Jump back to start
        self.instructions.append(IRInstruction("JMP", [start_label]))

        # Mark end of loop
        self.instructions.append(IRInstruction("LABEL", [end_label]))

    def visit_function_declaration(self, stmt: FunctionStmt) -> None:
        # Save previous function context if any
        prev_function = self.current_function
        self.current_function = stmt.name.lexeme

        func_start_label = self.new_label()
        func_end_label = self.new_label()

        # Skip over function body when it's defined
        self.instructions.append(IRInstruction("JMP", [func_end_label]))

        # Function body starts here
        self.instructions.append(IRInstruction("LABEL", [func_start_label]))

        # Define function - name and parameter count
        self.instructions.append(IRInstruction("FUNC", [stmt.name.lexeme, len(stmt.params)]))

        # Process parameters - they'll be popped in the order they were pushed
        for param in stmt.params:
            self.instructions.append(IRInstruction("PARAM", [param.lexeme]))

        # Generate function body
        for statement in stmt.body:
            self.visit_statement(statement)

        # Make sure we have a return at the end
        self.instructions.append(IRInstruction("CONST", [None]))  # Default return value
        self.instructions.append(IRInstruction("RETURN"))

        # Function definition ends here
        self.instructions.append(IRInstruction("LABEL", [func_end_label]))

        # Store function object
        self.instructions.append(IRInstruction("CONST", [func_start_label]))
        self.instructions.append(IRInstruction("STORE", [stmt.name.lexeme]))

        # Restore previous function context
        self.current_function = prev_function

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
        else:
            raise RuntimeError(f"Unsupported unary operator: {expr.operator.type}")

    def visit_logical(self, expr: Logical) -> None:
        if expr.operator.type == "OR":
            # Short-circuit OR: if left is true, skip right
            end_label = self.new_label()
            self.visit_expression(expr.left)
            self.instructions.append(IRInstruction("DUP"))
            self.instructions.append(IRInstruction("JMP_TRUE", [end_label]))
            self.instructions.append(IRInstruction("POP"))
            self.visit_expression(expr.right)
            self.instructions.append(IRInstruction("LABEL", [end_label]))
        elif expr.operator.type == "AND":
            # Short-circuit AND: if left is false, skip right
            end_label = self.new_label()
            self.visit_expression(expr.left)
            self.instructions.append(IRInstruction("DUP"))
            self.instructions.append(IRInstruction("JMP_FALSE", [end_label]))
            self.instructions.append(IRInstruction("POP"))
            self.visit_expression(expr.right)
            self.instructions.append(IRInstruction("LABEL", [end_label]))
        else:
            raise RuntimeError(f"Unsupported logical operator: {expr.operator.type}")

    def new_label(self) -> str:
        self.label_counter += 1
        return f"L{self.label_counter}"