from .dumper import CodeDumper
from .helpers import format_code, get_name_from_obj, get_source_from_obj

__all__ = ['CodeDumper', 'pretty_print', 'dump']


def pretty_print(obj, with_source=True, with_vars=True,
                 with_result=True, with_logs=False):
    source = get_source_from_obj(obj)
    name_ = get_name_from_obj(obj)

    if with_source:
        print("Source")
        print('======')
        print(format_code(source))
        print()

    if with_logs:
        import logging
        logging.basicConfig(level=logging.DEBUG)
    cd = CodeDumper(source)

    if with_vars:
        print('Variables')
        print('=========')

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

        print()

    result = cd.dump(name_)
    if with_result:
        print("Result")
        print("======")
        print(format_code(result))
        print()


def dump(obj):
    source = get_source_from_obj(obj)
    name = get_name_from_obj(obj)
    return CodeDumper(source).dump(name)
