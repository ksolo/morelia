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
        print(f"[DEBUG Compiler.__init__] Initialized: module_code=[]")
        
    def compile_file(self, input_path: Path, output_path: Path) -> None:
        """Compile a Python file to LLVM IR."""
        # Read and parse the source file
        with open(input_path, 'r') as f:
            source = f.read()

        # ---- ADDED DEBUG BLOCK ----
        print(f"\n[DEBUG Compiler.compile_file] Raw source code read from '{input_path}' (first 500 chars):")
        print(f"{repr(source[:500])}")
        print(f"[DEBUG Compiler.compile_file] Length of raw source code: {len(source)}\n")
        # ---- END DEBUG BLOCK ----
    
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
            
            print(f"[DEBUG Compiler.compile_file] visitor.get_llvm_ir() before write: {visitor.get_llvm_ir()}")
            
            # Write LLVM IR to file
            with open(output_path, 'w') as f:
                f.write(visitor.get_llvm_ir())
            
            print(f"Successfully compiled {input_path} to {output_path}")
            
        except Exception as e:
            print(f"Compilation failed: {str(e)}")
            raise
            
    def compile_to_llvm(self, source: str) -> str:
        """Compile Python source to LLVM IR."""
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
        print(f"[DEBUG Compiler.compile_to_llvm] Creating LLVMIRGenerator instance.")
        visitor = LLVMIRGenerator() # LLVMIRGenerator from ast_visitor.py
        print(f"[DEBUG Compiler.compile_to_llvm] LLVMIRGenerator instance created, ID: {id(visitor)}, type: {type(visitor)}")
        
        print(f"[DEBUG Compiler.compile_file] About to call visitor.visit(ast_module)")
        visitor.visit(ast_module)
        print(f"[DEBUG Compiler.compile_file] Finished visitor.visit(ast_module)")
        
        llvm_ir_code = visitor.get_llvm_ir()
        print(f"\n[DEBUG Compiler.compile_file] FINAL llvm_ir_code (direct print, first 300 chars):\n{llvm_ir_code[:300]}\n")
        print(f"[DEBUG Compiler.compile_file] FINAL llvm_ir_code (repr print, first 300 chars):\n{repr(llvm_ir_code[:300])}\n")

        with output_path.open('w', encoding='utf-8') as f:
            f.write(llvm_ir_code)
        print(f"[DEBUG Compiler.compile_file] Finished f.write(visitor.get_llvm_ir())")

        return llvm_ir_code
