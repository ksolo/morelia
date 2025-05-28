"""
Morelia compiler - Converts Python to LLVM IR.
"""

import ast
from pathlib import Path
from typing import Optional
from .type_checker import TypeChecker
from .ast_visitor import LLVMIRGenerator

class MoreliaCompiler:
    """Python to LLVM IR compiler."""
    
    def __init__(self):
        self.module_code = []
        
    def compile_file(self, input_path: Path, output_path: Path) -> None:
        """Compile a Python file to LLVM IR."""
        # Read and parse the source file
        with open(input_path, 'r') as f:
            source = f.read()

        try:
            # Parse the source code
            ast_module = ast.parse(source)
            
            # Pre-process type annotations
            for node in ast.walk(ast_module):
                if isinstance(node, ast.FunctionDef):
                    if isinstance(node.returns, ast.Constant) and node.returns.value is None:
                        node.returns = ast.Name(id='None', ctx=ast.Load())
            
            # Type check the code
            type_checker = TypeChecker()
            if not type_checker.check(ast_module):
                raise TypeError("Type checking failed:\n" + "\n".join(type_checker.errors))
            
            # Generate LLVM IR
            visitor = LLVMIRGenerator()
            visitor.visit(ast_module)
            
            # Write LLVM IR to file
            with open(output_path, 'w') as f:
                f.write(visitor.get_llvm_ir())
            
            print(f"Successfully compiled {input_path} to {output_path}")
            
        except Exception as e:
            print(f"Compilation failed: {str(e)}")
            raise
