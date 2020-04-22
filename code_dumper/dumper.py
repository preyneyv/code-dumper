import ast
from typing import Iterable, Set

from code_dumper.attribute_adder import AttributeAdder
from code_dumper.finder import NodeFinder
from code_dumper.helpers import get_name_nodes, log, log_return
from code_dumper.memory import MemoryVariable
from code_dumper.parser import Parser
from code_dumper.types import variable_scope_nodes
from code_dumper.variables import VariableReference, VariableScopeMap


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
        self.source = source.split('\n')
        self.root = ast.parse(source)

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

    def _calculate_node_dependencies(self):
        """
        Add dependencies for all nodes. The dependencies will be a list of var
        contexts to be used when resolving dependencies down the line.
        This has to be done after the variable scopes are populated.
        """
        for node in ast.walk(self.root):
            dependencies = set(get_name_nodes(node, loads=True,
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
            # Also get all sub-dependencies if node is a scope.
            # if isinstance(node, variable_scope_nodes):
            #     node.subdependencies = list(dep for dep in dependencies
            #                                 if dep.var_scope is node)

    def dump(self, name: str) -> str:
        """
        Dump the given object's source code.
        :return: The source code as a string
        """
        log("Dumping `%s`", name)
        root_scp = self.scope_map.get(self.root)
        if name not in root_scp:
            raise ValueError("Tried to dump variable `{}` which does not exist "
                             "in the global scope.".format(name))

        var = root_scp.get(name)

        line_numbers = set()
        loaded = []

        for mv in var:
            target = mv.definition
            self.parser.parse_target(target)
            line_numbers.update(self._resolve_stmt_dependencies(target, loaded))

        return self._get_code_from_lines(line_numbers)

        # if isinstance(obj, FunctionType):
        #     *_, target = self.finder.find(nf_type=ast.FunctionDef,
        #                                   qualname=obj.__qualname__)

    def _resolve_stmt_dependencies(self, stmt: ast.stmt, loaded: list = None,
                                   depth=0) -> Set[int]:
        loaded = loaded or []
        name = stmt
        if isinstance(stmt, variable_scope_nodes):
            name = f"`{stmt.qualname}`"
        if stmt in loaded:
            log('Skipping L%d: %s', stmt.lineno, name, depth=depth)
            return log_return(set(), depth)

        loaded.append(stmt)
        log('Loading L%d: %s', stmt.lineno, name, depth=depth)

        # Add this statement's parent block's line numbers.
        pb = stmt
        while pb.parent_block:
            pb = pb.parent_block
        line_numbers = set(range(*self._get_line_interval(pb)))

        refs = set()
        for n in ast.walk(stmt):
            # Include only the resolved VariableReferences.
            refs.update(dep for dep in n.dependencies
                        if isinstance(dep, VariableReference))

        variables = set(mv for ref in refs for mv in ref)
        for variable in variables:
            line_numbers.update(
                self._resolve_variable_dependencies(variable, loaded,
                                                    depth + 1))

        return log_return(line_numbers, depth)

    def _resolve_variable_dependencies(self, mv: MemoryVariable,
                                       loaded: list = None, depth=0) -> Set[
        int]:
        """
        Fetch all the lines that need to be present for this MemoryVariable to
        exist.
        :param mv: The target MemoryVariable.
        :param loaded:
        :param depth: The current recursion depth, used for pretty debug logs.
        :return:
        """
        loaded = loaded or []
        if mv in loaded:
            log('Skipping variable %s', mv, depth=depth)
            return log_return(set(), depth)

        loaded.append(mv)
        log('Loading variable %s', mv, depth=depth)

        line_numbers = set()
        for stmt in mv:
            # Fetch the parent block for importing.
            line_numbers.update(
                self._resolve_stmt_dependencies(stmt, loaded, depth + 1))

        return log_return(line_numbers, depth)

    def _find_min_max_lines(self, nodes: Iterable[ast.AST]) -> (int, int):
        """
        Find the lowest and highest line number in nodes.
        :param nodes: Iterable of nodes to check
        :return: The lowest and highest line numbers found
        """
        min_lineno = len(self.source) + 1
        max_lineno = 0

        for node in nodes:
            if hasattr(node, "lineno"):
                min_lineno = min(min_lineno, node.lineno)
                max_lineno = max(max_lineno, node.lineno)

        return min_lineno, max_lineno + 1

    def _get_line_interval(self, target: ast.AST,
                           from_lineno: int = None) -> (int, int):
        """
        Return every line starting at the node and ending at the beginning of
        the next.
        :param target: The node to traverse.
        :return: The lowest and highest line numbers.
        """
        sorted_siblings = sorted(
            filter(lambda x: hasattr(x, 'lineno'),
                   ast.iter_child_nodes(target.parent)),
            key=lambda x: x.lineno)
        from_lineno = from_lineno or target.lineno
        try:
            next_sibling = sorted_siblings[sorted_siblings.index(target) + 1]
            if next_sibling.lineno == from_lineno:
                return from_lineno, from_lineno + 1
            return from_lineno, next_sibling.lineno
        except IndexError:
            if target.parent == self.root:
                return from_lineno, len(self.source) + 1
            return self._get_line_interval(target.parent, from_lineno)

    def _get_code_from_lines(self, line_numbers: Set[int]) -> str:
        """
        Convert the given line numbers into the corresponding lines of code.
        :param line_numbers: The line numbers to get
        :return: The corresponding lines from the code, with common indents
            removed.
        """
        # Sort the line numbers
        lines = sorted(list(line_numbers))
        # Get the lines
        code = [self.source[idx - 1] for idx in lines]
        # Strip the common indent from the start of all lines.
        common_indent = min(len(line) - len(line.lstrip())
                            for line in code if not line.isspace())
        trimmed_lines = (line[common_indent:] for line in code)
        # Join into a single string
        return '\n'.join(trimmed_lines)
