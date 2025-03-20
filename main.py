#!/usr/bin/env python3

import sys
from lexer import Lexer
from parser import Parser
from interpreter import Interpreter

def run_file(file_path):
    with open(file_path, 'r') as file:
        run(file.read())

def run_prompt():
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

def run(source, interpreter=None):
    if interpreter is None:
        interpreter = Interpreter()

    # Lexical analysis: Convert source code to tokens
    lexer = Lexer(source)
    tokens = lexer.scan_tokens()

    # Syntax analysis: Parse tokens into an AST
    parser = Parser(tokens)
    statements = parser.parse()

    # If there was a syntax error, don't continue to evaluation
    if not statements:
        return

    # Execute the program
    interpreter.interpret(statements)

def main():
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