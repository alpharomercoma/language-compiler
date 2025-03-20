from typing import List, Dict, Any, Tuple
from ir_generator import IRInstruction

class VirtualMachine:
    def __init__(self):
        self.stack: List[Any] = []
        self.globals: Dict[str, Any] = {}
        self.labels: Dict[str, int] = {}
        self.call_stack: List[Tuple[int, Dict[str, Any]]] = []
        self.ip = 0  # Instruction pointer

    def load_instructions(self, instructions: List[IRInstruction]) -> None:
        self.instructions = instructions
        self.ip = 0
        self.stack = []
        self.globals = {}
        self.call_stack = []

        # First pass: collect all labels
        for i, instr in enumerate(instructions):
            if instr.opcode == "LABEL":
                self.labels[instr.operands[0]] = i

    def run(self) -> None:
        while self.ip < len(self.instructions):
            instruction = self.instructions[self.ip]
            self.ip += 1  # Move to next instruction

            self.execute_instruction(instruction)

    def execute_instruction(self, instruction: IRInstruction) -> None:
        opcode = instruction.opcode
        operands = instruction.operands

        # Stack operations
        if opcode == "CONST":
            self.stack.append(operands[0])
        elif opcode == "POP":
            self.stack.pop()
        elif opcode == "DUP":
            value = self.stack[-1]
            self.stack.append(value)

        # Variable operations
        elif opcode == "LOAD":
            name = operands[0]
            if name not in self.globals:
                raise RuntimeError(f"Undefined variable: {name}")
            self.stack.append(self.globals[name])
        elif opcode == "STORE":
            name = operands[0]
            value = self.stack.pop()
            self.globals[name] = value

        # Arithmetic operations
        elif opcode == "ADD":
            b = self.stack.pop()
            a = self.stack.pop()
            self.stack.append(a + b)
        elif opcode == "SUB":
            b = self.stack.pop()
            a = self.stack.pop()
            self.stack.append(a - b)
        elif opcode == "MUL":
            b = self.stack.pop()
            a = self.stack.pop()
            self.stack.append(a * b)
        elif opcode == "DIV":
            b = self.stack.pop()
            a = self.stack.pop()
            self.stack.append(a / b)
        elif opcode == "NEG":
            value = self.stack.pop()
            self.stack.append(-value)

        # Comparison operations
        elif opcode == "EQUAL":
            b = self.stack.pop()
            a = self.stack.pop()
            self.stack.append(a == b)
        elif opcode == "NOT_EQUAL":
            b = self.stack.pop()
            a = self.stack.pop()
            self.stack.append(a != b)
        elif opcode == "GREATER":
            b = self.stack.pop()
            a = self.stack.pop()
            self.stack.append(a > b)
        elif opcode == "GREATER_EQUAL":
            b = self.stack.pop()
            a = self.stack.pop()
            self.stack.append(a >= b)
        elif opcode == "LESS":
            b = self.stack.pop()
            a = self.stack.pop()
            self.stack.append(a < b)
        elif opcode == "LESS_EQUAL":
            b = self.stack.pop()
            a = self.stack.pop()
            self.stack.append(a <= b)

        # Logical operations
        elif opcode == "NOT":
            value = self.stack.pop()
            self.stack.append(not value)
        elif opcode == "AND":
            b = self.stack.pop()
            a = self.stack.pop()
            self.stack.append(a and b)
        elif opcode == "OR":
            b = self.stack.pop()
            a = self.stack.pop()
            self.stack.append(a or b)

        # Control flow operations
        elif opcode == "JMP":
            label = operands[0]
            if label in self.labels:
                self.ip = self.labels[label]
            else:
                raise RuntimeError(f"Unknown label: {label}")
        elif opcode == "JMP_FALSE":
            label = operands[0]
            condition = self.stack.pop()
            if not condition and label in self.labels:
                self.ip = self.labels[label]
            elif label not in self.labels:
                raise RuntimeError(f"Unknown label: {label}")
        elif opcode == "JMP_TRUE":
            label = operands[0]
            condition = self.stack.pop()
            if condition and label in self.labels:
                self.ip = self.labels[label]
            elif label not in self.labels:
                raise RuntimeError(f"Unknown label: {label}")

        # Function operations
        elif opcode == "CALL":
            func_name = operands[0]
            arg_count = operands[1]

            # Create a new scope for function variables
            saved_globals = self.globals.copy()

            if func_name in self.globals:
                # Get the function label
                func_label = self.globals[func_name]

                if isinstance(func_label, str) and func_label in self.labels:
                    # Save current position and globals on the call stack
                    self.call_stack.append((self.ip, saved_globals))

                    # Jump to function code
                    self.ip = self.labels[func_label]
                else:
                    # Call a built-in function
                    self.handle_builtin_function(func_name, arg_count)
            else:
                raise RuntimeError(f"Undefined function: {func_name}")
        elif opcode == "RETURN":
            return_value = self.stack.pop()

            if self.call_stack:
                # Restore execution context
                self.ip, saved_globals = self.call_stack.pop()

                # Restore global environment but keep any new globals
                temp_globals = self.globals
                self.globals = saved_globals

                # Add any new globals that were created
                for k, v in temp_globals.items():
                    if k not in saved_globals:
                        self.globals[k] = v

                # Push the return value onto the stack
                self.stack.append(return_value)
            else:
                # Top-level return, just continue
                self.stack.append(return_value)

        # Other operations
        elif opcode == "PRINT":
            value = self.stack.pop()
            print(value)
        elif opcode == "LABEL":
            # Labels are processed in the first pass, so do nothing here
            pass
        elif opcode == "FUNC":
            # Function declarations are handled by JMP and LABEL
            # Just skip the function parameters
            pass
        elif opcode == "PARAM":
            # Parameters are popped from the stack and stored as variables
            name = operands[0]
            if self.stack:
                value = self.stack.pop()
                self.globals[name] = value
        else:
            raise RuntimeError(f"Unknown instruction: {opcode}")

    def handle_builtin_function(self, func_name: str, arg_count: int) -> None:
        if func_name == "print":
            if arg_count != 1:
                raise RuntimeError("print() takes exactly 1 argument")
            value = self.stack.pop()
            print(value)
        else:
            raise RuntimeError(f"Unknown built-in function: {func_name}")