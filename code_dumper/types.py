import ast
from typing import Tuple, Type, Union

# These are the only nodes capable of defining a new variable scope.
variable_scope_nodes = ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef

# These are the nodes that have substatements.
code_block_nodes = (ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef,
                    ast.For, ast.AsyncFor, ast.While, ast.If, ast.With,
                    ast.AsyncWith, ast.Try)

# For type-hinting.
class T:
    VariableScopeNode = Union[ast.Module, ast.FunctionDef,
                              ast.ClassDef, ast.AsyncFunctionDef]
    NodeTupleOrNode = Union[Type[ast.AST], Tuple[Type[ast.AST], ...]]
