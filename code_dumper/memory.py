import ast
import itertools
from typing import List


class MemoryVariable:
    """
    A specific usage context for a specific variable within a specific scope.
    A MemoryVariable can only be defined once. All subsequent uses have to be
    mutations.
    """

    def __init__(self, address):
        """
        Create a new MemoryVariable.
        :param address: The memory address that this variable exists at.
        """
        self.address = address
        self.stores = []
        self.loads = []
        self.mutates = []

    @property
    def definition(self) -> ast.stmt:
        """
        The statement that defines this MemoryVariable.
        """
        return self.stores[0] if self.stores else None

    def add(self, type_name, source_node: ast.AST):
        if not isinstance(source_node, ast.stmt):
            source_node = source_node.find_ancestor(nf_type=ast.stmt)

        getattr(self, type_name).append(source_node)

    def __iter__(self):
        """
        Iterate over all of stores, loads, dels within a single iterator.
        :return: Iterator combining the values of stores, loads, and dels.
        """
        return itertools.chain(self.stores, self.loads, self.mutates)

    def __str__(self):
        return "{}".format(self.address)

    def clone(self):
        mv = MemoryVariable(self.address)
        mv.stores = self.stores.copy()
        mv.loads = self.loads.copy()
        mv.mutates = self.mutates.copy()
        return mv


class Memory:
    """
    Simulates the way programming languages work in terms of values vs
    references. Any variable will refer to an address which in turn refers to a
    MemoryVariable.
    """

    def __init__(self, mem=None):
        super().__init__()
        self._mem: List[MemoryVariable] = mem or []

    def new_address(self) -> MemoryVariable:
        address = len(self._mem)
        mv = MemoryVariable(address=address)
        self._mem.append(mv)
        return mv

    def get(self, addr) -> MemoryVariable:
        return self._mem[addr]

    def __repr__(self):
        return repr(self._mem)

    def __iter__(self):
        return iter(self._mem)

    def __len__(self):
        return len(self._mem)

    def clone(self):
        mem = [mv.clone() for mv in self._mem]
        return Memory(mem)
