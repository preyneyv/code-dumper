from .dumper import CodeDumper
from .helpers import get_source_from_obj

__all__ = ['CodeDumper', 'pretty_dump', 'dump']


def pretty_dump(obj, with_source=True):
    source = get_source_from_obj(obj)
    if with_source:
        print("Source")
        print('======')
        lines = source.split('\n')
        size = len(str(len(lines) + 1))
        def pad(ln):
            return ' ' * (size - len(str(ln))) + str(ln)
        print('\n'.join(
            "{}| {}".format(pad(ln), code) for ln, code in enumerate(source.split('\n'), 1)))
        print()
    print('Found Variables')
    print('===============')
    cd = CodeDumper(source)
    # cd.dump(obj)
    variables = cd.scope_map.get(cd.root)
    longest_name = max(len(k) for k in variables.keys())
    for name, ref in variables.items():
        lines = set()
        for var in ref:
            for stmt in var:
                lines.add(stmt.lineno)
        lines = map(str, sorted(list(lines)))
        formatted = ' ' * (longest_name - len(name)) + name

        print("{} -> {}".format(formatted, ', '.join(lines)))


def dump(obj):
    source = get_source_from_obj(obj)
    return CodeDumper(source).dump(obj)
