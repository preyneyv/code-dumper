import ast
from typing import Set, Iterable

from code_dumper.helpers import DefaultDictWithKey
from code_dumper.memory import MemoryVariable, Memory
from code_dumper.types import T


class VariableReference:
    def __init__(self, name=None, scope=None, variables=None):
        self.name = name
        self.scope: 'VariableScope' = scope
        self.variables: Set[MemoryVariable] = variables or set()

    def set(self, variables: Set[MemoryVariable], conditional=False):
        if conditional:
            self.variables.update(variables)
        else:
            self.variables = variables

    def add(self, type_name, source_node: ast.AST):
        for mv in self:
            mv.add(type_name, source_node)

    def get(self):
        return self.variables

    def __iter__(self) -> Iterable[MemoryVariable]:
        return iter(self.variables)

    def __str__(self):
        return '{}.{} >> {}'.format(self.scope, self.name,
                                    '/'.join(map(str, self.variables)))


class VariableScope(dict):
    """
    A scope in which identifiers can be defined.
    """

    def __init__(self, scp_map: 'VariableScopeMap',
                 scope_node: T.VariableScopeNode):
        """
        Create a new VariableScope instance, to be used to store all identifiers
        in this scope.
        """
        super().__init__()
        self.map = scp_map
        self.scope_node = scope_node

    def get(self, name: str, inherit_from_parent=True) -> VariableReference:
        if name not in self:
            mvs = None
            if inherit_from_parent:
                # The identifier doesn't exist in this scope, so we need to
                # copy the MemoryVariable from an outer scope and inherit it.
                scp = self.map.find_parent_scope(self, name)
                mvs = scp.get(name, inherit_from_parent=False).get()
                if not mvs:
                    mvs = scp.new(name, False).get()
            self[name] = VariableReference(name=name, scope=self,
                                           variables=mvs)

        return self[name]

    def alias(self, target: str, source: str, conditional) -> VariableReference:
        src = self.get(source)
        tgt = self.get(target, inherit_from_parent=False)
        tgt.set(src.get(), conditional)
        self[target] = tgt
        return tgt

    def new(self, name: str, conditional) -> VariableReference:
        """
        Create a memory variable for the identifier.
        """
        mv = self.map.memory.new_address()
        vr = self.get(name, inherit_from_parent=False)
        vr.set({mv}, conditional)
        return vr

    def __str__(self):
        node = self.scope_node
        if isinstance(node, ast.Module):
            return '<source>'
        if node is False:
            return '<external>'
        return "{}.{}".format('<source>', node.qualname)

    def import_from_parent(self, name: str, from_global=False):
        """
        Clone a variable from a parent scope into this one.
        :param name: Name of the variable to clone.
        :param from_global: Whether to import only from the global scope or
            to work backwards until a variable is found.
        """
        if from_global:
            scp = self.map.get(self.map.root)
        else:
            scp = self.map.find_parent_scope(self, name)
        self[name] = scp.get(name)


class VariableScopeMap:
    """
    Manages a representation of variables in their corresponding scopes, along
    with its creations, loads, and deletions.

    Disambiguation:
      "VariableScope" refers to a node scope, one that can only be created by a
        Module, ClassDef, FunctionDef, or AsyncFunctionDef.
      "VariableUsageContext" refers to the usage of any variable in a specific
        context. For instance, the usage of the variable `x` within the
        function do_something_amazing(). VariableUsageContexts can and will be
        aliased when globals or nonlocals are used. They also have a property
        `inherits` which refers back to the original context.
    """

    def __init__(self, root):
        """
        Create a new VariableScopeMap.
        """
        self.root = root
        self.memory = Memory()
        self.scope_map = DefaultDictWithKey(
            lambda scope_node: VariableScope(scp_map=self,
                                             scope_node=scope_node))

    def get(self, scope_node) -> VariableScope:
        """
        Find and return the VariableScope for the provided scope node.
        :param scope_node: The node on which the scope exists.
        :return: The corresponding VariableScope object, or a new one if it
            doesn't exist.
        """
        return self.scope_map[scope_node]

    def get_from_name(self, name_node: ast.Name) -> VariableReference:
        return self.get(name_node.var_scope).get(name_node.id,
                                                 inherit_from_parent=True)

    def find_parent_scope(self, starting_scope: VariableScope,
                          identifier: str) -> VariableScope:
        """
        Find the scope that defines the identifier for the first time.
        :param starting_scope: The scope on which the identifier currently
            exists.
        :param identifier: The identifier to search for.
        :return: The nearest ancestor that defines the identifier.
        """
        scope = starting_scope.scope_node
        while scope and identifier not in self.get(scope):
            # get the parent scope
            scope = scope.var_scope
        return self.get(scope)
