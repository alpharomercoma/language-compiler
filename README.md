# Simple Language Interpreter

A simple programming language interpreter implemented in Python. This project demonstrates the fundamental concepts of compiler design and implementation.

## Features

- Lexical Analysis (Tokenization)
- Syntax Analysis (Parsing)
- Semantic Analysis
- Intermediate Code Generation
- Virtual Machine Execution

### Language Features

- Variables and assignments
- Basic arithmetic operations (+, -, *, /)
- Comparison operators (==, !=, >, >=, <, <=)
- Logical operators (and, or, not)
- Control flow (if/else, while loops)
- Function definitions and calls
- Built-in print function

## Project Structure

- `main.py` - Main entry point and REPL
- `lexer.py` - Tokenizes source code
- `parser.py` - Parses tokens into AST
- `semantic_analyzer.py` - Performs semantic analysis
- `ir_generator.py` - Generates intermediate code
- `virtual_machine.py` - Executes intermediate code
- `examples/` - Example programs

## Usage

### Running a File

```bash
python main.py examples/fibonacci.txt
```

### Interactive REPL

```bash
python main.py
```

## Example Programs

### Simple Arithmetic
```python
var x = 5;
var y = 3;
print(x + y);  // Prints: 8
```

### Fibonacci Sequence
```python
fun fibonacci(n) {
    if (n <= 1) return n;
    return fibonacci(n - 1) + fibonacci(n - 2);
}

var i = 0;
while (i < 10) {
    print(fibonacci(i));
    i = i + 1;
}
```

## Implementation Details

1. **Lexical Analysis**: Converts source code into tokens
2. **Syntax Analysis**: Builds an Abstract Syntax Tree (AST)
3. **Semantic Analysis**: Validates types and program correctness
4. **Intermediate Code Generation**: Creates a sequence of instructions
5. **Virtual Machine**: Executes the intermediate code

## Error Handling

The interpreter provides clear error messages for:
- Syntax errors
- Type errors
- Undefined variables
- Runtime errors

## Future Improvements

- [ ] Add more built-in functions
- [ ] Support for arrays and dictionaries
- [ ] Object-oriented features
- [ ] Standard library
- [ ] Optimization passes
- [ ] Better error reporting
- [ ] Debugging support

## License

MIT License