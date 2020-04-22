from code_dumper import pretty_print

def target():
    print('first')

if True:
    def target():
        print('second')


y = 3
a = 3
b = 4
x = a + b

def target():
    return x

if True:
    def target():
        return y

pretty_print(target)
