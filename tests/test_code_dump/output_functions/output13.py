#########################     INPUT     ##############################
def my_gen():
    n = 1
    print('This is printed first')
    yield n

    n += 1
    print('This is printed second')
    yield n

    n += 1
    print('This is printed at last')
    yield n

x=my_gen()
next(x)
next(x)

## Input Object to dump function : my_gen

#########################     INPUT ENDS HERE     ##############################


#########################     OUTPUT     ##############################
def my_gen():
    n = 1
    print('This is printed first')
    yield n

    n += 1
    print('This is printed second')
    yield n

    n += 1
    print('This is printed at last')
    yield n

x=my_gen()#########################     OUTPUT ENDS HERE     ##############################
