from code_dumper import pretty_print

x = 4


def mult(y):
    f = lambda y: y + x
    return f(y)


pretty_print(mult, with_source=0, with_logs=1)
