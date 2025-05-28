"""
Command-line interface for Morelia compiler.
"""

from typing import Optional

import click
from pathlib import Path
from .compiler import MoreliaCompiler

@click.group()
def cli():
    """Morelia - Python to LLVM IR compiler."""
    pass

@cli.command(name="compile")
@click.argument('input_file', type=click.Path(exists=True, dir_okay=False))
@click.option('--output', '-o', type=click.Path(dir_okay=False),
              help='Output file path (default: input file with .ll extension)')
def compile_command(input_file: str, output: Optional[str] = None):
    """Compiles a Python file to LLVM IR code."""
    input_path = Path(input_file)
    
    # Determine output path
    if output is None:
        output_path = input_path.with_suffix('.ll')
    else:
        output_path = Path(output)
    
    # Create compiler and compile
    compiler = MoreliaCompiler()
    try:
        compiler.compile_file(input_path, output_path)
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        raise click.Abort()

if __name__ == '__main__':
    cli()
