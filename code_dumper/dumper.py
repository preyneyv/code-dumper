import ast
import inspect
import logging
from typing import Union

from IPython import get_ipython

from code_dumper.attribute_adder import AttributeAdder
from code_dumper.finder import NodeFinder
from code_dumper.helpers import get_name_nodes
from code_dumper.parser import Parser
from code_dumper.variables import VariableScopeMap, VariableScope

logger = logging.getLogger('Code Dumper')


class CodeDumper:
    """
        Given a target function/class, dump only the minimum amount of source
        code needed for the target to work properly, stripping unnecessary
        function definitions, variables, and import statements.
        """

    def __init__(self, source):
        """
        Create a CodeDumper instance to dump the minimum amount of code needed
        for the target `obj` to run successfully.
        """
        # Get module source and build the AST
        self.source = source
        self.root = ast.parse(''.join(self.source))

        # Instantiate a finder to help find nodes easier.
        self.finder = NodeFinder(self.root)

        # Modify the AST with attributes that help us achieve the objective.
        AttributeAdder(self.root).visit(self.root)

        # Add a .dependencies attribute on every node. This has to happen after
        # AttributeAdder runs, because it needs node.var_scope.
        self._calculate_node_dependencies()

        # Create a VariableScopeMap to track every variable.
        self.scope_map = VariableScopeMap(self.root)

        # Construct our understanding of the code.
        self.parser = Parser(self.root, self.scope_map)

        # self.finder: Optional[NodeFinder] = None
        # self.scope_map: Optional[VariableScopeMap] = None

    def dump(self, obj) -> str:
        """
        Dump the given object's source code.
        :return: The source code as a string
        """
        logger.debug("Dumping %s", obj)

        return 'x'

    def _calculate_node_dependencies(self):
        """
        Add dependencies for all nodes. The dependencies will be a list of var
        contexts to be used when resolving dependencies down the line.
        This has to be done after the variable scopes are populated.
        """
        for node in ast.walk(self.root):
            dependencies = set(get_name_nodes(node, loads=True,
                                              ignore_root=True))
            if isinstance(node, ast.AugAssign):
                # Even stores are dependencies.
                dependencies.update(get_name_nodes(node, stores=True,
                                                   ignore_root=True))

            # Fix the scope for decorators, base classes, defaults.
            # It should be set to the parent scope of node, not the node itself.
            to_fix_scopes = []
            if hasattr(node, 'decorator_list'):
                to_fix_scopes.extend(node.decorator_list)
            if hasattr(node, 'bases'):
                to_fix_scopes.extend(node.bases)
            if hasattr(node, 'args'):
                if isinstance(node.args, ast.arguments):
                    to_fix_scopes.extend(node.args.defaults)

            for to_fix in to_fix_scopes:
                for name in get_name_nodes(to_fix, loads=True,
                                           ignore_root=False):
                    name.var_scope = node.var_scope
                    dependencies.add(name)

            # This array contains everything that needs to be pulled in from
            # outside in order to execute this body of code.
            node.dependencies = list(dep for dep in dependencies
                                     if dep.var_scope is node.var_scope)
