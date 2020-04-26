a='kes'
def my_func():
    global a
    print(a)
    a='rit'
    print(a)
b='global'
def my_func_outer():
    my_func()
    b='local'
