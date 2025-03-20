#!/usr/bin/env python3

import sys
from typing import List
from lexer import Lexer, Token
from parser import Parser, Stmt
from interpreter import Interpreter
from semantic_analyzer import SemanticAnalyzer

def run_file(file_path: str) -> None:
    with open(file_path, 'r') as file:
        run(file.read())

def run_prompt() -> None:
    interpreter = Interpreter()

    while True:
        try:
            line = input("> ")
            if not line:
                break
            run(line, interpreter)
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")

def run(source: str, interpreter: Interpreter = None) -> None:
    if interpreter is None:
        interpreter = Interpreter()

    # Lexical analysis: Convert source code to tokens
    lexer = Lexer(source)
    tokens: List[Token] = lexer.scan_tokens()

    # Syntax analysis: Parse tokens into an AST
    parser = Parser(tokens)
    statements: List[Stmt] = parser.parse()

    # If there was a syntax error, don't continue to evaluation
    if not statements:
        return

    # Semantic analysis: Check types and validate program
    analyzer = SemanticAnalyzer()
    if not analyzer.analyze(statements):
        return

    # Execute the program
    interpreter.interpret(statements)

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