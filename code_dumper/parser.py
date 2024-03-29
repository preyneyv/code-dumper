import ast
from typing import Union

from code_dumper.finder import NodeFinder
from code_dumper.helpers import get_name_nodes, log
from code_dumper.variables import VariableScope, VariableScopeMap


class Parser:
    """
    Parse an AST to build an understanding of variables, their usages,
    redeclarations, etc.
    """

    def __init__(self, root: ast.Module, scope_map: VariableScopeMap):
        """
        Instantiate a new Parser.
        :param root: The root node to start parsing from.
        :param scope_map: The scope map to update with values.
        """
        self.root = root
        self.scope_map = scope_map
        self.finder = NodeFinder(root)

        self.parsed = []

        # Parse the statements
        scp = self.scope_map.get(self.root)
        for stmt in self.root.body:
            self._parse_stmt(stmt, scp, conditional=False)

    def _parse_stmt(self, stmt: ast.stmt, scp: VariableScope, conditional):
        """
        Given a statement, call its corresponding handler, then handle its
        dependencies.
        :param stmt: The statement to be parsed.
        :param scp: The variable scope to be used.
        :param conditional: Whether any variable changes should be treated as
            conditional or guaranteed.
        """
        if stmt in self.parsed:
            return log("Parser: Already parsed L%d: %s", stmt.lineno, stmt)
        log("Parser: Parsing L%d: %s", stmt.lineno, stmt)
        self.parsed.append(stmt)

        # Call the appropriate handler.
        if isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef)):
            self._parse_function_def(stmt, scp, conditional)

        if isinstance(stmt, ast.ClassDef):
            self._parse_class_def(stmt, scp, conditional)

        if isinstance(stmt, (ast.Import, ast.ImportFrom)):
            self._parse_import(stmt, scp, conditional)

        if isinstance(stmt, (ast.Assign, ast.AnnAssign)):
            self._parse_assign(stmt, scp, conditional)

        if isinstance(stmt, ast.AugAssign):
            self._parse_aug_assign(stmt, scp, conditional)

        if isinstance(stmt, (ast.Global, ast.Nonlocal)):
            self._parse_scope_changer(stmt, scp, conditional)

        if isinstance(stmt, (ast.For, ast.AsyncFor)):
            self._parse_for(stmt, scp, conditional)

        if isinstance(stmt, ast.While):
            self._parse_while(stmt, scp, conditional)

        if isinstance(stmt, ast.If):
            self._parse_if(stmt, scp, conditional)

        if isinstance(stmt, (ast.With, ast.AsyncWith)):
            self._parse_with(stmt, scp, conditional)

        self._parse_dependencies(stmt, scp, conditional)

    def _parse_dependencies(self, stmt, scp, conditional):
        # Convert all name dependencies into VariableReferences
        deps = set()
        for name in stmt.dependencies:
            identifier = scp.get(name.id)
            deps.add(identifier)
            call = name.find_ancestor(nf_type=ast.Call)
            if call and call.root_name == name:
                # This dependency is being called. We should figure out what it
                # does to our variable scopes (if we have access to its source).
                # NOTE: This does not look at methods and stuff, please fix.
                # If a class constructor is being called, check cls.__init__
                for mv in identifier:
                    definition = mv.definition
                    if definition is None:
                        # We don't have the source code.
                        continue
                    if isinstance(definition, ast.FunctionDef):
                        # It's a function.
                        self._parse_function_body(definition, conditional,
                                                  call=call)

        stmt.dependencies = deps

    def _parse_function_def(self, stmt: Union[ast.FunctionDef,
                                              ast.AsyncFunctionDef],
                            scp: VariableScope, conditional: bool):
        # Only define the function variable. The actual code execution only
        # happens when the function is called.
        scp.new(stmt.name, conditional).add('stores', stmt)

    def _parse_class_def(self, stmt: ast.ClassDef, scp: VariableScope,
                         conditional: bool):
        # Add the class definition to the current scope.
        scp.new(stmt.name, conditional).add('stores', stmt)

        # Get the class scope.
        scp_ = self.scope_map.get(stmt)

        # Parse its body.
        for stmt_ in stmt.body:
            self._parse_stmt(stmt_, scp_, conditional)

    def _parse_import(self, stmt: Union[ast.Import, ast.ImportFrom],
                      scp: VariableScope, conditional: bool):
        for alias in stmt.names:
            # import tensorflow.keras -> name == 'tensorflow'
            # import numpy as np -> name == 'np'
            # from tensorflow.keras import Sequential -> name == 'Sequential'
            name = (alias.asname or alias.name).split('.')[0]
            scp.new(name, conditional).add("stores", stmt)

    def _parse_assign(self, stmt: Union[ast.Assign, ast.AnnAssign],
                      scp: VariableScope, conditional: bool):
        # KNOWN ISSUES:
        # - List/tuple unpacking does not properly assign the memory
        #   addresses to their corresponding variables.
        for target in stmt.targets:
            if isinstance(target, ast.Name):
                # Assignment to a single variable.
                if isinstance(stmt.value, ast.Name):
                    # It's a variable aliasing. [a = b]
                    tgt = scp.alias(target.id, stmt.value.id, conditional)
                else:
                    # It's anything else. [a = 4], [a = b.test]
                    tgt = scp.new(target.id, conditional)
                tgt.add('stores', stmt)
                continue

            for var in self.finder.find(nf_type=(ast.Subscript,
                                                 ast.Attribute),
                                        nf_root=target, ctx=ast.Store):
                # It's a mutation [a.b = 3], [a['f'] = 4]
                if isinstance(var.root_name, ast.Name):
                    # Get the variable and add a mutation.
                    scp.get(var.root_name.id).add('mutates', stmt)

            for var in get_name_nodes(target, stores=True):
                # It's a direct assignment [a = 4], [a, b = 1, 2]
                scp.new(var.id, conditional).add('stores', stmt)

    def _parse_aug_assign(self, stmt: ast.AugAssign, scp: VariableScope,
                          conditional: bool):
        # Treat AugAssigns as mutations. Although, technically speaking,
        # it's only a mutation if the data is a non-primitive type, it's
        # easier and accurate enough for our use-case to handle all
        # AugAssigns as mutations.
        if isinstance(stmt.target, ast.Name):
            # [lst += [4]] [x += 1]
            target = scp.get(stmt.target.id)
        else:
            # [a.b += 4] [a['b'] += amazing_var]
            target = scp.get(stmt.target.root_name.id)
        target.add('mutates', stmt)

    def _parse_scope_changer(self, stmt: Union[ast.Global, ast.Nonlocal],
                             scp: VariableScope, conditional: bool):
        # Link from an outer scope into the current one.
        from_global = isinstance(stmt, ast.Global)
        for name in stmt.names:
            scp.import_from_parent(name, from_global)

    def _parse_for(self, stmt: Union[ast.For, ast.AsyncFor],
                   scp: VariableScope, conditional: bool):
        # Get all variables that the loop writes to.
        for var in get_name_nodes(stmt.target, stores=True):
            scp.new(var.id, conditional).add('stores', stmt)

        # Parse its body. Conditional because the loop might never run.
        for stmt_ in (stmt.body + stmt.orelse):
            self._parse_stmt(stmt_, scp, conditional=True)

    def _parse_while(self, stmt: ast.While, scp: VariableScope,
                     conditional: bool):
        # Parse its body. Conditional because the loop might never run.
        for stmt_ in (stmt.body + stmt.orelse):
            self._parse_stmt(stmt_, scp, conditional=True)

    def _parse_if(self, stmt: ast.If, scp: VariableScope,
                  conditional: bool):
        # Parse its body. Conditional because the body might never run.
        for stmt_ in (stmt.body + stmt.orelse):
            self._parse_stmt(stmt_, scp, conditional=True)

    def _parse_with(self, stmt: Union[ast.With, ast.AsyncWith],
                    scp: VariableScope, conditional: bool):
        # Assign the variables that `with` defines.
        for item in stmt.items:
            for name in get_name_nodes(item, stores=True):
                scp.new(name.id, conditional).add('stores', stmt)

        # Parse its body.
        for stmt_ in stmt.body:
            self._parse_stmt(stmt_, scp, conditional)

    def _parse_function_body(self, target: ast.FunctionDef, conditional: bool,
                             call: ast.Call = None):
        if target.body in self.parsed:
            return log("Parser: Already parsed body L%d: %s",
                       target.lineno, target)
        log("Parser: Parsing body L%d: %s", target.lineno, target)
        self.parsed.append(target)

        # Get the new scope.
        scp = self.scope_map.get(target)

        # Define all the arguments as variables.
        names = set()

        consolidated = [
            *(target.args.args if hasattr(target.args, 'args') else []),
            *(target.args.posonlyargs if hasattr(target.args, 'posonlyargs') else []),
            *(target.args.kwonlyargs if hasattr(target.args, 'kwonlyargs') else []),
            *([target.args.vararg] if target.args.vararg else []),
            *([target.args.kwarg] if target.args.kwarg else []),
        ]
        for arg in consolidated:
            if arg.arg in names:
                continue
            scp.new(arg.arg, conditional).add("stores", target)
            names.add(arg.arg)

        # Store before state
        before = self.scope_map.memory.clone()

        # Parse its body.
        for stmt in target.body:
            self._parse_stmt(stmt, scp, conditional)

        if not call:
            return

        # Find the changes caused by "executing" the function body and link
        # them back to the initial ast.Call so we know to include it later.
        for i, new_mv in enumerate(self.scope_map.memory):
            if i >= len(before):
                # It's a new thing defined by this function.
                new_mv.add('stores', call)
                continue
            old_mv = before.get(i)
            if set(old_mv) != set(new_mv):
                # There's been a mutation
                new_mv.add('mutates', call)

    def _parse_class_body(self, target: ast.ClassDef, conditional: bool):
        """
        "Execute" all methods of the class.
        """
        if target.body in self.parsed:
            return log("Parser: Already parsed body L%d: %s",
                       target.lineno, target)
        log("Parser: Parsing body L%d: %s", target.lineno, target)
        self.parsed.append(target)

        for stmt in target.body:
            # Only include methods.
            if not isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue

            self._parse_function_body(stmt, conditional)

    def parse_target(self, target: ast.stmt):
        log("Parser: Parsing target L%d: %s", target.lineno, target)

        if isinstance(target, (ast.FunctionDef, ast.AsyncFunctionDef)):
            return self._parse_function_body(target, False)

        if isinstance(target, ast.ClassDef):
            return self._parse_class_body(target, False)

        raise TypeError('Tried to parse unknown target type %s' % type(target))
