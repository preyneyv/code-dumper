import ast
from functools import partial
from typing import Union

from code_dumper.finder import NodeFinder
from code_dumper.types import code_block_nodes, variable_scope_nodes


class AttributeAdder(ast.NodeVisitor):
    """
    Add custom attributes to AST nodes to make usage easier.
    Added:
     - node.parent          -> Reference to parent node.
     - node.parent_block    -> Reference to parent code block (e.g.
                               if-statement, loop, function).
     - node.var_scope       -> The variable scope this node exists in.
     - node.find_ancestor() -> Find the first ancestor node that matches the
                               query. Returns False if none found.
     On FunctionDefs,
       - qualname           -> The qualified name, equivalent to `__qualname__`
                               on a function.
       - ismethod           -> Whether the function belongs to a class or is
                               standalone.
     On ClassDef,
       - qualname           -> The qualified name, equivalent to `__qualname__`
                            on a class.
    """

    def __init__(self, root):
        super().__init__()
        self.root = root
        self.qualname_stack = []

    @staticmethod
    def find_ancestor(node, nf_type=None, **properties) -> Union[ast.AST, bool]:
        """
        Finds the first ancestor of `node` that meets the necessary criteria.
        Returns False if none found.
        :param node: The node to start the search from.
        :param nf_type: The type of node to search for.
        :param properties: Properties to search for. Refer to
            `NodeFinder.matches` for details.
        :return: The found ancestor or False if none found.
        """
        n = node
        while hasattr(n, 'parent'):
            n = n.parent
            if NodeFinder.matches(n, nf_type=nf_type, **properties):
                return n
        return False

    def visit(self, node):
        for child in ast.iter_child_nodes(node):
            # Add the parent ref.
            child.parent = node
        # Bind `self.find_ancestor` to `node` and add it as a property.
        node.find_ancestor = partial(self.find_ancestor, node)

        # Add variable scopes.
        node.var_scope = node.find_ancestor(variable_scope_nodes) or self.root
        if node == self.root:
            node.var_scope = False

        # Add parent code block
        node.parent_block = node.find_ancestor(code_block_nodes)

        super().visit(node)

    def visit_FunctionDef(self, node):
        self.qualname_stack.append(node.name)

        # Add the qualname to make finding a specific function easier.
        node.qualname = ".".join(self.qualname_stack)

        # Return whether the given function is a method or just a function.
        node.ismethod = isinstance(node.parent, ast.ClassDef)

        self.qualname_stack.append('<locals>')
        self.generic_visit(node)
        self.qualname_stack.pop()
        self.qualname_stack.pop()

    def visit_ClassDef(self, node):
        self.qualname_stack.append(node.name)

        # Add the qualname to make finding a specific class easier.
        node.qualname = ".".join(self.qualname_stack)

        self.generic_visit(node)
        self.qualname_stack.pop()

    def visit_Call(self, node):
        # Add the root object that the function is being called on
        # Ex: test_func()    -> obj_root: Name(test_func)
        #     amazing.test() -> obj_root: Name(amazing)
        #     a.b.c.d()      -> obj_root: Name(a)
        current = node.func
        path = []
        while isinstance(current, (ast.Attribute, ast.Subscript)):
            if isinstance(current, ast.Attribute):
                path.append(current.attr)
            else:
                path.append(current.slice)
            current = current.value
        path.append(current.id)
        node.root_name = current
        node.func_path = tuple(reversed(path))

        self.generic_visit(node)

    def visit_Subscript(self, node):
        root = node
        # Go to top of subscript/attribute chain.
        while isinstance(root, (ast.Subscript, ast.Attribute)):
            root = root.value
        node.root_name = root

        self.generic_visit(node)

    def visit_Attribute(self, node):
        return self.visit_Subscript(node)
