#!/usr/bin/env python3

import sys
from typing import List
from lexer import Lexer, Token
from parser import Parser, Stmt
from semantic_analyzer import SemanticAnalyzer
from ir_generator import IRGenerator, IRInstruction
from virtual_machine import VirtualMachine

def run_file(file_path: str) -> None:
    with open(file_path, 'r') as file:
        run(file.read())

def run_prompt() -> None:
    interpreter = VirtualMachine()

    while True:
        try:
            line = input("> ")
            if not line:
                break
            run(line)
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")

def run(source: str) -> None:
    # Lexical analysis: Convert source code to tokens
    lexer = Lexer(source)
    tokens: List[Token] = lexer.scan_tokens()

    # Syntax analysis: Parse tokens into an AST (abstract syntax tree)
    parser = Parser(tokens)
    statements: List[Stmt] = parser.parse()

    # If there was a syntax error, don't continue to evaluation
    if not statements:
        return

    # Semantic analysis: Check types and validate program
    analyzer = SemanticAnalyzer()
    if not analyzer.analyze(statements):
        return

    # Intermediate Code Generation (ICG)
    ir_generator = IRGenerator()
    instructions: List[IRInstruction] = ir_generator.generate(statements)

    # Debug: Print generated instructions
    debug_print_instructions(instructions)

    # Code Generation & Execution via Virtual Machine
    vm = VirtualMachine()
    vm.load_instructions(instructions)
    vm.run()

def debug_print_instructions(instructions: List[IRInstruction]) -> None:
    """Print IR instructions for debugging."""
    print("\n===== Generated IR Instructions =====")
    for i, instr in enumerate(instructions):
        print(f"{i:3d}: {instr}")
    print("====================================\n")

def main() -> None:
    args = sys.argv[1:]
    if len(args) > 1:
        print("Usage: main.py [script]")
        sys.exit(64)
    elif len(args) == 1:
        run_file(args[0])
    else:
        run_prompt()

if __name__ == "__main__":
    main()