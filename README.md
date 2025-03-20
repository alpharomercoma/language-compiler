# Simple Programming Language Compiler

A basic compiler implementation for a small programming language with support for variables, functions, loops, conditionals, and basic operations.

## Language Features

- **Data Types**: Numbers, strings, booleans
- **Variables**: `let` declarations with assignments
- **Control Flow**: `if/else` statements, `while` loops, `for` loops
- **Functions**: Function declarations, recursive functions
- **Operators**: Arithmetic, comparison, logical operations
- **I/O**: Basic `print` functionality

## Example Code

```
// Factorial function
function factorial(n) {
  if (n <= 1) {
    return 1;
  }
  return n * factorial(n - 1);
}

// Calculate factorial of 5
let result = factorial(5);
print result; // Should print 120
```

## Compiler Components

The compiler is structured into the following components:

1. **Lexer (`lexer.py`)**: Converts source code into tokens
2. **Parser (`parser.py`)**: Transforms tokens into an abstract syntax tree (AST)
3. **Interpreter (`interpreter.py`)**: Executes the AST

## Getting Started

### Prerequisites

- Python 3.6+

### Running the Compiler

To run the interpreter with a file:

```
python main.py examples/factorial.txt
```

To start an interactive REPL session:

```
python main.py
```

## Language Syntax

### Variable Declaration

```
let name = "value";
```

### Conditionals

```
if (condition) {
  // code
} else {
  // code
}
```

### Loops

```
while (condition) {
  // code
}

for (let i = 0; i < 10; i = i + 1) {
  // code
}
```

### Functions

```
function name(param1, param2) {
  // code
  return value;
}
```

## Implementation Details

- Recursive descent parser with Pratt parsing for expressions
- Environment-based variable scoping
- Support for closures and higher-order functions
- Error reporting with line numbers

## Future Enhancements

- Type checking and semantic analysis
- Optimization passes
- Bytecode or machine code generation
- Additional built-in functions and standard library