import ast
import inspect
import itertools

from IPython import get_ipython

from code_dumper.finder import NodeFinder


class DefaultDictWithKey(dict):
    """
    A custom implementation of collections.defaultdict which passes the key to
    the default_factory.
    """

    def __init__(self, default_factory):
        """
        Create an instance of DefaultDictWithKey with the provided
        default_factory.
        :param default_factory: The factory to create a new element in the dict.
        """
        super().__init__()
        self.default_factory = default_factory

    def __missing__(self, key):
        """
        If a key is missing, we call self.default_factory with the new key to be
        created.
        :param key: The key to be created.
        :return: The new entry.
        """
        self[key] = self.default_factory(key)
        return self[key]


def get_name_nodes(root, loads=False, stores=False,
                   dels=False, ignore_root=False):
    """
    Get all sub-nodes of type ast.Name.
    :param root: Root to start the search from.
    :param loads: Whether to include ctx=ast.Load.
    :param stores: Whether to include ctx=ast.Store.
    :param dels: Whether to include ctx=ast.Del.
    :param ignore_root: Whether to include the root node in the results.
    :return: Generator that returns the matched nodes.
    """
    try:
        iter(root)
        return itertools.chain(
            *[get_name_nodes(r, loads, stores, dels, ignore_root)
              for r in root]
        )
    except TypeError:
        ...

    ctxs = (
        *((ast.Load,) if loads else tuple()),
        *((ast.Store,) if stores else tuple()),
        *((ast.Del,) if dels else tuple())
    )
    finder = NodeFinder(root)
    return itertools.chain(
        *[finder.find(nf_type=ast.Name, nf_ignore_root=ignore_root, ctx=ctx)
          for ctx in ctxs]
    )


def get_source_from_obj(obj):
    """
    Get the source code for the file in which obj is defined, or the entire
    IPython kernel, depending on the environment.
    :param obj: The target object to be dumped.
    :return: All the source lines from the environment.
    """
    kernel = get_ipython()
    if kernel:
        # Use _ih to get all code run in the kernel.
        # Not using kernel.ev('_ih') because we don't want to modify the input
        # history.
        source = '\n# ---\n'.join(kernel.history_manager.input_hist_parsed)
    else:
        # Use `inspect` to get all the source code of the module.
        mod = inspect.getmodule(obj)
        source = inspect.getsource(mod)
    return source
