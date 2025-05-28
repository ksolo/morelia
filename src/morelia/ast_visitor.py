"""
AST visitor for generating LLVM IR.
"""

from typing import Any, Dict, Optional, List
# Ensure all necessary ast node types are imported
import ast # Using 'import ast' is cleaner

print("\n[DEBUG_CANARY] >>> ast_visitor.py module is being imported/executed! <<<\n")


class LLVMIRGenerator(ast.NodeVisitor): # Inherit from ast.NodeVisitor
    """Generate LLVM IR from Python AST."""
    
    def __init__(self):
        self.module_prefix_code: List[str] = []
        self.global_definitions: List[str] = []
        self.all_function_definitions_code: List[str] = []
        self.current_function_body_code: List[str] = []
        
        self.variables: Dict[str, str] = {}
        self.current_function_name: Optional[str] = None
        self.block_counter = 0
        
        self.module_prefix_code.append("declare i32 @printf(i8*, ...)")

    def _escape_llvm_string(self, py_string: str) -> str:
        escaped = ""
        if not isinstance(py_string, str):
            # This case should ideally not be hit if type checking is done prior,
            # or if visit_Constant only processes actual string constants.
            py_string = str(py_string) # Fallback

        for char_code in py_string.encode('utf-8'):
            # For LLVM, non-printable characters and certain special characters
            # need to be escaped as '\\XX' where XX is the hex code.
            if char_code == ord('\\'):
                escaped += '\\5C'  # Backslash itself
            elif char_code == ord('"'):
                escaped += '\\22'  # Double quote
            elif char_code == ord('\n'):
                escaped += '\\0A'  # Newline
            elif char_code == ord('\r'):
                escaped += '\\0D'  # Carriage Return
            elif char_code == ord('\t'):
                escaped += '\\09'  # Tab
            # Check for other non-printable ASCII characters (0-31 and 127)
            # or characters that might need escaping in LLVM strings.
            elif not (32 <= char_code <= 126):
                escaped += f'\\{char_code:02X}' # General hex escape for non-printable or >126
            else:
                escaped += chr(char_code) # Directly append printable ASCII characters
        return escaped

    def _map_ast_annotation_to_llvm(self, annotation_node: Optional[ast.AST]) -> str:
        if annotation_node is None:
            return "void"
        if isinstance(annotation_node, ast.Name):
            if annotation_node.id == 'None':
                return "void"
            elif annotation_node.id == 'int':
                return "i32"
            elif annotation_node.id == 'str':
                return "i8*" # Assuming strings are char pointers
        if isinstance(annotation_node, ast.Constant) and annotation_node.value is None:
            return "void"
        
        return "void" # Default for unhandled annotations

    def visit_Module(self, node: ast.Module) -> None:
        first_node_is_docstring = False
        if node.body:
            first_node = node.body[0]
            if isinstance(first_node, ast.Expr) and \
               isinstance(first_node.value, ast.Constant) and \
               isinstance(first_node.value.value, str):
                first_node_is_docstring = True

        for i, body_node in enumerate(node.body):
            if i == 0 and first_node_is_docstring:
                continue
            self.visit(body_node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> Any:
        self.current_function_name = node.name
        self.current_function_body_code = ["entry:"]

        args_str = "" # Placeholder: Implement argument handling based on node.args

        llvm_return_type = "void" # Default
        if node.name == "main":
            llvm_return_type = "i32"
        elif node.returns: 
            llvm_return_type = self._map_ast_annotation_to_llvm(node.returns)
        else:
            pass

        func_signature_str = f"define {llvm_return_type} @{node.name}({args_str}) {{"
        
        for stmt in node.body:
            if isinstance(stmt, ast.Expr) and \
               isinstance(stmt.value, ast.Constant) and \
               isinstance(stmt.value.value, str):
                continue
            self.visit(stmt)

        last_instr_is_terminator = False
        if len(self.current_function_body_code) > 1: 
            last_line = self.current_function_body_code[-1].strip()
            if last_line.startswith("ret ") or \
               last_line.startswith("br ") or \
               last_line.startswith("unreachable"):
                last_instr_is_terminator = True
        
        if not last_instr_is_terminator:
            if node.name == "main":
                self.current_function_body_code.append("  ret i32 0")
            elif llvm_return_type == "void":
                self.current_function_body_code.append("  ret void")
            else:
                self.current_function_body_code.append(f"  ret {llvm_return_type} zeroinitializer")

        current_full_function_code_lines: List[str] = [] 
        current_full_function_code_lines.append(func_signature_str)
        current_full_function_code_lines.extend(self.current_function_body_code)
        current_full_function_code_lines.append("}")
        
        self.all_function_definitions_code.extend(current_full_function_code_lines)
        
        self.current_function_name = None
        self.current_function_body_code = []

    def visit_Constant(self, node: ast.Constant) -> Any:
        value = node.value

        if isinstance(value, str):
            string_name = f"str_{self.block_counter}"
            self.block_counter += 1
            
            escaped_value = self._escape_llvm_string(value)
            null_terminator_llvm = r"\00"
            # Use byte length of the original Python string for size calculation
            # as LLVM's array size is in bytes. Add 1 for null terminator.
            llvm_str_len = len(value.encode('utf-8')) + 1
            
            global_str_def = f"@{string_name} = private unnamed_addr constant [{llvm_str_len} x i8] c\"{escaped_value}{null_terminator_llvm}\", align 1"
            
            self.global_definitions.append(global_str_def)
            
            result = f"i8* getelementptr inbounds ([{llvm_str_len} x i8], [{llvm_str_len} x i8]* @{string_name}, i32 0, i32 0)"
            return result
        
        elif isinstance(value, (int, float)):
            # For LLVM, int constants are just numbers. Floats need type (e.g. double)
            if isinstance(value, float):
                return f"double {value}" # LLVM float syntax
            return str(value) # For int
        
        elif value is None:
            # 'None' as a value doesn't directly translate to an LLVM instruction operand in most cases.
            # It's often implicit in 'void' types or 'null' for pointers.
            return "null ; Representing Python None as null pointer or in void context" 

        return f"; Unhandled Constant: {value}"

    def visit_Call(self, node: ast.Call) -> Any:
        if isinstance(node.func, ast.Name) and node.func.id == 'print':
            
            if not node.args: # Handle print() with no arguments
                newline_char_name = "global_newline_for_empty_print"
                
                py_newline_str = "\n" # Python string for newline
                escaped_llvm_newline = self._escape_llvm_string(py_newline_str) # Should produce "\0A"
                null_terminator_llvm = r"\\00" # LLVM IR null terminator
                # Length of "\n" is 1 byte. Total LLVM string length is 1 (for \0A) + 1 (for \00) = 2 bytes.
                newline_llvm_len = len(py_newline_str.encode('utf-8')) + 1 

                newline_def = f"@{newline_char_name} = private unnamed_addr constant [{newline_llvm_len} x i8] c\\\"{escaped_llvm_newline}{null_terminator_llvm}\\\", align 1"
                
                is_defined = False
                for gd in self.global_definitions:
                    if newline_def == gd: 
                        is_defined = True
                        break
                if not is_defined:
                    self.global_definitions.append(newline_def)
                
                printf_call = f"  call i32 @printf(i8* getelementptr inbounds ([{newline_llvm_len} x i8], [{newline_llvm_len} x i8]* @{newline_char_name}, i32 0, i32 0))"
                self.current_function_body_code.append(printf_call)
                return printf_call

            # Handle print("string literal") directly
            elif len(node.args) == 1 and isinstance(node.args[0], ast.Constant) and isinstance(node.args[0].value, str):
                py_string_literal = node.args[0].value
                string_with_newline = py_string_literal + "\n" # Append Python newline

                temp_ast_node = ast.Constant(value=string_with_newline)
                # self.visit(temp_ast_node) will call visit_Constant, which creates the global string
                # (including 'align 1') and returns the GEP expression.
                llvm_ptr_to_combined_string = self.visit(temp_ast_node) 
                
                printf_call = f"  call i32 @printf({llvm_ptr_to_combined_string})"
                
                self.current_function_body_code.append(printf_call)
                return printf_call
            
            else: # Fallback for print(variable), print(expression), or multiple/non-string arguments
                
                if not node.args: # Should be caught by empty print() case, but safeguard here.
                    self.current_function_body_code.append("  ; ERROR: Fallback print logic with no arguments")
                    return "; ERROR: Fallback print logic with no arguments"

                format_str_content_py = "%s\n" 
                format_name = f"fmt_{self.block_counter}" 

                escaped_format_content_llvm = self._escape_llvm_string(format_str_content_py)
                null_terminator_llvm = r"\\00" 
                format_str_llvm_len = len(format_str_content_py.encode('utf-8')) + 1

                format_str_def = f"@{format_name} = private unnamed_addr constant [{format_str_llvm_len} x i8] c\\\"{escaped_format_content_llvm}{null_terminator_llvm}\\\", align 1"
                
                is_defined = False
                for gd in self.global_definitions:
                    if format_str_def == gd:
                        is_defined = True
                        break
                if not is_defined:
                     self.global_definitions.append(format_str_def)
                     self.block_counter += 1 
                else:
                    pass

                # This currently only handles the first argument for simplicity.
                # A robust solution for multiple arguments would iterate node.args,
                # build a combined format string (e.g., "%s %s\n"), and pass all GEPs.
                arg_llvm_value = self.visit(node.args[0]) 

                printf_call = f"  call i32 @printf(i8* getelementptr inbounds ([{format_str_llvm_len} x i8], [{format_str_llvm_len} x i8]* @{format_name}, i32 0, i32 0), {arg_llvm_value})"
                
                self.current_function_body_code.append(printf_call)
                return printf_call
        
        # If not a 'print' call, handle other function calls
        if isinstance(node.func, ast.Name):
            call_placeholder = f"  ; Placeholder for call to function @{node.func.id}"
            self.current_function_body_code.append(call_placeholder)
            # For now, assume non-void functions need a placeholder result if used in an expression.
            # This is a major simplification. A real compiler needs type info.
            return f"%call_result_placeholder_for_{node.func.id} ; Placeholder return value for {node.func.id}"
        
        unhandled_call_msg = "; Call to unhandled complex callable (e.g., attribute access, subscript)"
        self.current_function_body_code.append(f"  {unhandled_call_msg}")
        return unhandled_call_msg 

    def visit_Return(self, node: ast.Return) -> Any:
        if node.value:
            llvm_value = self.visit(node.value)
            if self.current_function_name == "main": 
                ret_instr = f"  ret i32 {llvm_value}"
            else:
                # This needs to fetch the actual LLVM return type of the current function
                # For now, this is a simplification. A proper type system is needed.
                # Let's assume it's void if not main and value is None, otherwise use value directly.
                # This part needs to align with visit_FunctionDef's llvm_return_type logic.
                # A more robust way: current_func_llvm_type = self._get_llvm_type_for_current_func_return()
                # For now, if node.value is None (Python None), it should be 'ret void'
                # if the function is void. If function is i32, it should be 'ret i32 <val>'.
                # This is a known simplification point.
                # Defaulting to trying to use the value, assuming it's correctly typed by previous visits.
                # This will likely fail if the function is void and returns a value, or vice-versa.
                # A better way: check the expected LLVM type from visit_FunctionDef.
                func_node = None # Need to get current function's AST node to check its return type annotation
                # This is complex. For now, a simpler approach:
                # If the value is 'null ; ... None', and func is void, then 'ret void'.
                # If func is i32, 'ret i32 <llvm_value>'.
                # This is a known simplification point.
                ret_instr = f"  ret void ; Placeholder for non-main return, value: {llvm_value}"
                # A more robust approach would be:
                # current_func_llvm_return_type = self._get_current_function_llvm_return_type() # Helper needed
                # ret_instr = f"  ret {current_func_llvm_return_type} {llvm_value}"

            self.current_function_body_code.append(ret_instr)
        else: # Return with no value (e.g. 'return' in a function typed as -> None)
            if self.current_function_name == "main":
                self.current_function_body_code.append("  ret i32 0") 
            else:
                self.current_function_body_code.append("  ret void") 
        return None 

    def get_llvm_ir(self) -> str:
        """Assemble and return the full LLVM IR code."""
        
        full_code_lines = []
        full_code_lines.extend(self.module_prefix_code)
        if self.global_definitions: # Add a newline only if there are global defs
            full_code_lines.append("") 
        full_code_lines.extend(self.global_definitions)
        if self.all_function_definitions_code: # Add a newline only if there are functions
            full_code_lines.append("") 
        full_code_lines.extend(self.all_function_definitions_code)
        
        final_code = "\n".join(full_code_lines)
        return final_code

    # Placeholder for other necessary visit methods (e.g., visit_Assign, visit_Name, etc.)
    def visit_Name(self, node: ast.Name) -> Any:
        # This is a very basic placeholder. Variable handling (load/store) is complex.
        # For now, if it's a load, return a placeholder LLVM variable name.
        if isinstance(node.ctx, ast.Load):
            return f"%{node.id} ; Placeholder for loaded variable"
        return f"; Unhandled Name context for {node.id}"

    def generic_visit(self, node: ast.AST) -> Any:
        super().generic_visit(node)