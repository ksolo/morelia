# Morelia - Python to LLVM Compiler

Morelia is a Python compiler that converts Python code with type hints into native executables using the LLVM toolchain.

## Features

- Compile Python code with type hints to LLVM IR
- Generate optimized native executables
- Support for basic arithmetic operations
- Type-safe compilation
- Multiple optimization levels
- Error handling and debugging support

## Installation

### Using Docker

The easiest way to get started with Morelia is using Docker:

```bash
# Build the Docker image
docker build -t morelia .

# Run the compiler
docker run -v $(pwd):/app morelia compile your_program.py
```

### Local Development

1. Clone the repository:
```bash
git clone https://github.com/yourusername/morelia.git
cd morelia
```

2. Install dependencies using uv:
```bash
# Initialize uv environment
uv init

# Install dependencies
uv pip install -e .
```

3. Verify installation:
```bash
morelia --version
```

## Usage

### Basic Compilation

```bash
# Compile a Python file
morelia compile your_program.py

# Specify output file
morelia compile your_program.py --output your_program.out

# Enable optimizations
morelia compile your_program.py --optimize 3

# Enable debug mode
morelia compile your_program.py --debug
```

### Example

Here's a simple example of a Python program that can be compiled:

```python
# example.py
def add(a: int, b: int) -> int:
    return a + b

result = add(42, 24)
print(result)
```

To compile this example:

```bash
morelia compile example.py
```

## Development

### Setting Up Development Environment

1. Install system dependencies:
```bash
# Install LLVM tools
apt-get update && apt-get install -y clang llvm lld libclang-dev

# Install Python dependencies
uv pip install -e .
```

2. Run tests:
```bash
# Run all tests
pytest tests/

# Run specific test
pytest tests/test_compiler.py::test_sample_compilation
```

3. Run with debug output:
```bash
morelia compile example.py --debug
```

### Code Style and Formatting

Morelia uses Ruff for code formatting and linting. The configuration is in `pyproject.toml`.

To format code:
```bash
ruff check .
ruff format .
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- LLVM Project for the LLVM toolchain
- Python Software Foundation for Python
- All contributors who have helped with this project