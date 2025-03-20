from typing import List, Dict, Any
from code_generator import Bytecode

class VM:
    def __init__(self) -> None:
        self.code: bytes = b""
        self.constants: List[Any] = []
        self.stack: List[Any] = []
        self.globals: Dict[str, Any] = {}
        self.functions: Dict[str, int] = {}  # function name -> start address
        self.ip: int = 0  # instruction pointer
        self.sp: int = 0  # stack pointer

    def run(self, bytecode: Bytecode) -> None:
        self.code = bytecode.code
        self.constants = bytecode.constants
        self.stack = []
        self.globals = {}
        self.functions = {}
        self.ip = 0
        self.sp = 0

        while self.ip < len(self.code):
            opcode = self.code[self.ip]
            self.ip += 1

            if opcode == 0:  # OP_CONST
                const_idx = self.code[self.ip]
                self.ip += 1
                self.push(self.constants[const_idx])
            elif opcode == 1:  # OP_LOAD
                name_idx = self.code[self.ip]
                self.ip += 1
                name = self.constants[name_idx]
                if name not in self.globals:
                    raise RuntimeError(f"Undefined variable: {name}")
                self.push(self.globals[name])
            elif opcode == 2:  # OP_STORE
                name_idx = self.code[self.ip]
                self.ip += 1
                name = self.constants[name_idx]
                value = self.pop()
                self.globals[name] = value
            elif opcode == 3:  # OP_ADD
                b = self.pop()
                a = self.pop()
                self.push(a + b)
            elif opcode == 4:  # OP_SUB
                b = self.pop()
                a = self.pop()
                self.push(a - b)
            elif opcode == 5:  # OP_MUL
                b = self.pop()
                a = self.pop()
                self.push(a * b)
            elif opcode == 6:  # OP_DIV
                b = self.pop()
                a = self.pop()
                self.push(a / b)
            elif opcode == 7:  # OP_PRINT
                value = self.pop()
                print(value)
            elif opcode == 8:  # OP_JMP
                target = self.code[self.ip]
                self.ip += 1
                self.ip = target
            elif opcode == 9:  # OP_JMP_FALSE
                target = self.code[self.ip]
                self.ip += 1
                if not self.pop():
                    self.ip = target
            elif opcode == 10:  # OP_CALL
                name_idx = self.code[self.ip]
                self.ip += 1
                name = self.constants[name_idx]
                if name not in self.functions:
                    raise RuntimeError(f"Undefined function: {name}")
                # Save current IP and jump to function
                self.push(self.ip)
                self.ip = self.functions[name]
            elif opcode == 11:  # OP_RETURN
                if self.sp > 0:
                    self.ip = self.pop()
                else:
                    return
            elif opcode == 12:  # OP_FUNC
                name_idx = self.code[self.ip]
                self.ip += 1
                name = self.constants[name_idx]
                self.functions[name] = self.ip
                # Skip function body until return
                while self.ip < len(self.code) and self.code[self.ip] != 11:
                    self.ip += 1
                self.ip += 1
            elif opcode == 13:  # OP_PARAM
                name_idx = self.code[self.ip]
                self.ip += 1
                name = self.constants[name_idx]
                value = self.pop()
                self.globals[name] = value
            elif opcode == 14:  # OP_NEG
                value = self.pop()
                self.push(-value)
            elif opcode == 15:  # OP_NOT
                value = self.pop()
                self.push(not value)
            elif opcode == 16:  # OP_OR
                b = self.pop()
                a = self.pop()
                self.push(a or b)
            elif opcode == 17:  # OP_AND
                b = self.pop()
                a = self.pop()
                self.push(a and b)

    def push(self, value: Any) -> None:
        self.stack.append(value)
        self.sp += 1

    def pop(self) -> Any:
        self.sp -= 1
        return self.stack.pop()