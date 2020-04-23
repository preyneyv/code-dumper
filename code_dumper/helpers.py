import ast
import inspect
import itertools
import logging
import types

from IPython import get_ipython

from code_dumper.finder import NodeFinder

logger = logging.getLogger('Code Dumper')
INDENT = ' │'


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


def can_be_parsed(cell):
    """
    Check if code is syntactically accurate by attempting to create an AST. Note
    :param cell:
    :return:
    """
    try:
        ast.parse(cell)
    except:
        return False
    return True


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
        all_history = kernel.history_manager.input_hist_parsed
        # We only want syntactically valid history cells.
        filtered_history = filter(can_be_parsed, all_history)
        source = '\n# ---\n'.join(filtered_history)
    else:
        # Use `inspect` to get all the source code of the module.
        mod = inspect.getmodule(obj)
        source = inspect.getsource(mod)
    return source


def get_name_from_obj(obj) -> str:
    """
    Convert the given object into an identifier name.
    """
    if isinstance(obj, types.FunctionType):
        return obj.__name__
    if isinstance(obj, type):
        return obj.__name__

    raise ValueError(f"No reliable way to get original variable name from type"
                     f"{type(obj)}.")


def format_code(code):
    """
    Add line numbers to code for pretty printing
    """
    lines = code.split('\n')
    size = len(str(len(lines) + 1))

    def pad(ln):
        return ' ' * (size - len(str(ln))) + str(ln)

    return '\n'.join(
        "{}| {}".format(pad(ln), code) for ln, code in
        enumerate(code.split('\n'), 1))


def log(msg, *args, depth=0):
    """
    Write to the debug logs.
    """
    logger.debug("%s " + msg, INDENT * depth, *args)


def log_return(ret_val, depth=0):
    """
    Write a return value to the debug logs.
    """
    log("└── %s", ret_val, depth=depth)
    return ret_val
