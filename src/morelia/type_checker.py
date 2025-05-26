"""
Type checker for Morelia compiler.
"""

from typing import Any, Dict, Optional
from ast import NodeVisitor, FunctionDef, Return, Name, Constant, Call

class TypeChecker(NodeVisitor):
    """Type checker for Python code."""
    
    def __init__(self):
        self.errors: list[str] = []
        self.variables: Dict[str, type] = {} # Stores user-defined variables and their types
        # self.builtins stores recognized built-in names.
        # For types like 'None', the value is the type itself (type(None)).
        # For functions like 'print', the value can be a sentinel (e.g., None) 
        # or a more complex structure if we were checking signatures.
        self.builtins: Dict[str, Any] = {
            'print': None,          # Sentinel for the print function
            'None': type(None),     # Represents the None type
            'NoneType': type(None), # Alias for the None type
            'int': int              # Represents the integer type
        }
        print(f"[DEBUG TypeChecker.__init__] Initialized builtins: {self.builtins}")
        
    def visit_FunctionDef(self, node: FunctionDef) -> Any:
        """Visit a function definition."""
        print(f"[DEBUG TypeChecker.visit_FunctionDef] START Visiting FuncDef: {node.name}, Line: {node.lineno}")
        # Check return type annotation
        if not node.returns:
            self.errors.append(f"Function {node.name} lacks return type annotation")
            return
            
        # Get return type
        return_type = self._get_type_annotation(node.returns)
        print(f"[DEBUG TypeChecker.visit_FunctionDef] After _get_type_annotation for '{node.name}', return_type is: {return_type} (type: {type(return_type)})")
        if return_type is None:
            print(f"[DEBUG TypeChecker.visit_FunctionDef] TypeError: return_type is None for function {node.name}")
            self.errors.append(f"Invalid return type annotation for function {node.name}")
            return
            
        # Manually visit statements in the function body
        print(f"[DEBUG TypeChecker.visit_FunctionDef] START Visiting body of {node.name}")
        for stmt in node.body:
            self.visit(stmt)
        print(f"[DEBUG TypeChecker.visit_FunctionDef] END Visiting body of {node.name}")
        
    def visit_Name(self, node: Name) -> Any:
        """Visit a variable name (e.g., in an expression or as a function call target).
        Type names in annotations are handled by _get_type_annotation.
        """
        print(f"[DEBUG TypeChecker.visit_Name] Visiting Name: {node.id}, Line: {node.lineno}, Col: {node.col_offset}")
        node_id = node.id

        # ABSOLUTELY CRITICAL FIRST CHECK:
        # If this method is ever called with a Name node where id is 'None' or 'NoneType',
        # it must be treated as a valid type identifier and not an undefined variable.
        # This is the most direct safeguard against the "Undefined variable: None" error.
        if node_id == 'None' or node_id == 'NoneType':
            return # It's a recognized type name, not an undefined variable.

        # If not 'None' or 'NoneType', then check if it's another recognized built-in (e.g., 'print').
        # self.builtins contains 'print', and also 'None'/'NoneType' (which are caught above).
        if node_id in self.builtins:
            # This will catch 'print' or any other built-ins we might add.
            return # Recognized built-in, not an undefined variable.

        # If it's not 'None', 'NoneType', or any other name in self.builtins,
        # it must be a user-defined variable. Check if it has been defined.
        if node_id not in self.variables:
            self.errors.append(f"Undefined variable: {node_id}")
            # The error is recorded. The TypeChecker.check() method will return False.

        # If the name is a known variable or a recognized built-in/type name, no error is appended.
            
    def visit_Constant(self, node: Constant) -> Any:
        """Visit a constant value."""
        # Allow string constants (e.g., "Hello, World!") and None constants.
        if isinstance(node.value, (str, int)) or node.value is None:
            return
        # Other constant types (int, float, bool) in expressions would be caught here if not handled.
        # For hello_world.py, only string literals and None (as a type hint) are relevant constants.
        self.errors.append(f"Unsupported constant type: {type(node.value).__name__}")
            
    def visit_Call(self, node: Call) -> Any:
        """Visit a function call."""
        if isinstance(node.func, Name):
            func_name = node.func.id
            if func_name == 'print':
                # Allow any type for print arguments
                return
            elif func_name in self.variables:
                # Check function call with user-defined function
                return
            else:
                self.errors.append(f"Undefined function: {func_name}")
        self.generic_visit(node)
            
    def _get_type_annotation(self, annotation: Any) -> Optional[type]:
        """Get type from annotation."""
        print(f"[DEBUG TypeChecker._get_type_annotation] START _get_type_annotation. Input: {annotation} (type: {type(annotation)})")
        if isinstance(annotation, Name):
            type_name = annotation.id
            print(f"[DEBUG _get_type_annotation] Annotation is Name, id='{type_name}'")
            if type_name in self.builtins:
                print(f"[DEBUG _get_type_annotation] '{type_name}' is in self.builtins.")
                val = self.builtins[type_name]
                print(f"[DEBUG _get_type_annotation] Builtin value for '{type_name}' is: {val} (type: {type(val)})")
                if val is type(None):
                    print(f"[DEBUG _get_type_annotation] Recognized Name '{type_name}' as type(None). Returning type(None).")
                    return type(None)
                # For 'None' or 'NoneType', self.builtins[type_name] is type(None)
                # For 'print', self.builtins[type_name] is None (sentinel)
                # For other types like 'int', it would be the type itself if added.
                return self.builtins[type_name]
            else:
                print(f"[DEBUG _get_type_annotation] Fallback for Name: Unsupported type annotation: {type_name}")
                self.errors.append(f"Unsupported type annotation: {type_name}")
                return None
        elif isinstance(annotation, Constant) and annotation.value is None:
            # This case should ideally not be hit if compiler pre-processing is active,
            # but handle as a fallback.
            return type(None) # Or self.builtins.get('None') which is type(None)
        
        print(f"[DEBUG _get_type_annotation] Fallback: Unknown annotation type: {type(annotation)}")
        self.errors.append(f"Unknown annotation type: {type(annotation)}")
        return None
            
    def check(self, node: Any) -> bool:
        """Check the type of a node."""
        self.visit(node)
        return len(self.errors) == 0
