import ast

from code_dumper.types import T


class NodeFinder:
    """
    A query engine for Abstract Syntax Trees to make life easier when trying
    to find nodes.
    """

    def __init__(self, node: ast.AST):
        """
        Instantiate a new NodeFinder with `node` as the root node.
        :param node: The root node.
        """
        self.node = node

    @staticmethod
    def matches(node, nf_type: T.NodeTupleOrNode = None, **properties):
        """
        Check if `node` matches type `nf_type` and has attributes corresponding
        to `properties`.
        :param node: The node to be tested.
        :param nf_type: The desired node type.
        :param properties: kwargs containing the properties to be tested.
            NOTE: The attribute `ctx` expects the class of the desired type,
            not an instance.
            Example:
            ️ ✓ NodeFinder.matches(nf_type=ast.Name, ctx=ast.Load)
                    -> matches Name nodes with a context of ast.Load()
              ✗ NodeFinder.matches(nf_type=ast.Name, ctx=ast.Load())
                    -> does not work
        :return:
        """
        if nf_type and not isinstance(node, nf_type):
            return False

        # Test every property
        for attr, target in properties.items():
            if attr == 'ctx' and type(getattr(node, attr)) == target:
                continue
            if target != getattr(node, attr):
                return False
        return True

    def find(self, nf_type: T.NodeTupleOrNode = None, nf_root: ast.AST = None,
             nf_ignore_root=False, **properties):
        """
        Find all nodes matching the provided properties. Refer to
        `NodeFinder.matches` for a description of the property arguments.
        :param nf_type: Target node type.
        :param nf_root: Root node to start search from, optional. If not
            provided, self.node is used as the search root.
        :param nf_ignore_root: Whether the root node should be ignored from the
            search results.
        :param properties: The properties to match.
        :return: A generator returning the matching elements.
        """
        nf_root = nf_root or self.node
        for node in ast.walk(nf_root):
            if nf_ignore_root and node == nf_root:
                continue  # skip self

            if self.matches(node, nf_type, **properties):
                yield node
