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
git clone https://github.com/ksolo/morelia.git
cd morelia
```

2. Install dependencies using uv:
```bash
uv sync

```

## Usage

### Basic Compilation

```bash
# Compile a Python file
uv run python -m morelia.cli compile your_program.py

# Specify output file
uv run python -m morelia.cli compile your_program.py --output your_program.out
```

## Development

### Setting Up Development Environment

1. Install system dependencies:
```bash
# Install LLVM tools
apt-get update && apt-get install -y clang llvm lld libclang-dev

# Install Python dependencies
uv sync
```

2. Run tests:
```bash
# Run all tests
uv run pytest tests/

# Run specific test
uv run pytest tests/test_compiler.py::test_sample_compilation
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