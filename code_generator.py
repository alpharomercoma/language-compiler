from typing import List, Dict, Any
from ir_generator import IRInstruction

class Bytecode:
    def __init__(self, code: bytes, constants: List[Any] = None) -> None:
        self.code = code
        self.constants = constants or []

class CodeGenerator:
    def __init__(self) -> None:
        self.code: List[int] = []
        self.constants: List[Any] = []
        self.labels: Dict[str, int] = {}

    def generate(self, instructions: List[IRInstruction]) -> Bytecode:
        # First pass: collect labels
        for i, instr in enumerate(instructions):
            if instr.opcode == "LABEL":
                self.labels[instr.operands[0]] = i

        # Second pass: generate bytecode
        for instr in instructions:
            if instr.opcode == "CONST":
                self.emit_constant(instr.operands[0])
            elif instr.opcode == "LOAD":
                self.emit_load(instr.operands[0])
            elif instr.opcode == "STORE":
                self.emit_store(instr.operands[0])
            elif instr.opcode == "ADD":
                self.emit_add()
            elif instr.opcode == "SUB":
                self.emit_sub()
            elif instr.opcode == "MUL":
                self.emit_mul()
            elif instr.opcode == "DIV":
                self.emit_div()
            elif instr.opcode == "PRINT":
                self.emit_print()
            elif instr.opcode == "JMP":
                self.emit_jmp(instr.operands[0])
            elif instr.opcode == "JMP_FALSE":
                self.emit_jmp_false(instr.operands[0])
            elif instr.opcode == "CALL":
                self.emit_call(instr.operands[0])
            elif instr.opcode == "RETURN":
                self.emit_return()
            elif instr.opcode == "FUNC":
                self.emit_func(instr.operands[0])
            elif instr.opcode == "PARAM":
                self.emit_param(instr.operands[0])
            elif instr.opcode == "NEG":
                self.emit_neg()
            elif instr.opcode == "NOT":
                self.emit_not()
            elif instr.opcode == "OR":
                self.emit_or()
            elif instr.opcode == "AND":
                self.emit_and()
            elif instr.opcode == "LABEL":
                self.emit_label(instr.operands[0])

        return Bytecode(bytes(self.code), self.constants)

    def emit_constant(self, value: Any) -> None:
        self.code.append(0)  # OP_CONST
        self.constants.append(value)
        self.code.append(len(self.constants) - 1)

    def emit_load(self, name: str) -> None:
        self.code.append(1)  # OP_LOAD
        self.constants.append(name)
        self.code.append(len(self.constants) - 1)

    def emit_store(self, name: str) -> None:
        self.code.append(2)  # OP_STORE
        self.constants.append(name)
        self.code.append(len(self.constants) - 1)

    def emit_add(self) -> None:
        self.code.append(3)  # OP_ADD

    def emit_sub(self) -> None:
        self.code.append(4)  # OP_SUB

    def emit_mul(self) -> None:
        self.code.append(5)  # OP_MUL

    def emit_div(self) -> None:
        self.code.append(6)  # OP_DIV

    def emit_print(self) -> None:
        self.code.append(7)  # OP_PRINT

    def emit_jmp(self, label: str) -> None:
        self.code.append(8)  # OP_JMP
        target = self.labels[label]
        self.code.append(target)

    def emit_jmp_false(self, label: str) -> None:
        self.code.append(9)  # OP_JMP_FALSE
        target = self.labels[label]
        self.code.append(target)

    def emit_call(self, name: str) -> None:
        self.code.append(10)  # OP_CALL
        self.constants.append(name)
        self.code.append(len(self.constants) - 1)

    def emit_return(self) -> None:
        self.code.append(11)  # OP_RETURN

    def emit_func(self, name: str) -> None:
        self.code.append(12)  # OP_FUNC
        self.constants.append(name)
        self.code.append(len(self.constants) - 1)

    def emit_param(self, name: str) -> None:
        self.code.append(13)  # OP_PARAM
        self.constants.append(name)
        self.code.append(len(self.constants) - 1)

    def emit_neg(self) -> None:
        self.code.append(14)  # OP_NEG

    def emit_not(self) -> None:
        self.code.append(15)  # OP_NOT

    def emit_or(self) -> None:
        self.code.append(16)  # OP_OR

    def emit_and(self) -> None:
        self.code.append(17)  # OP_AND

    def emit_label(self, label: str) -> None:
        self.code.append(18)  # OP_LABEL
        self.constants.append(label)
        self.code.append(len(self.constants) - 1)