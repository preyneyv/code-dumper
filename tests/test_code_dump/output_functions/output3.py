#########################     INPUT     ##############################
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


## Input Object to dump function : my_func_outer

#########################     INPUT ENDS HERE     ##############################


#########################     OUTPUT     ##############################
def my_func():
    global a
    print(a)
    a='rit'
    print(a)
def my_func_outer():
    my_func()
    b='local'
#########################     OUTPUT ENDS HERE     ##############################
