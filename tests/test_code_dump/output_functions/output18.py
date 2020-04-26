#########################     INPUT     ##############################
from contextlib import contextmanager
def make_pretty(func):
    def inner():
        print("I got decorated")
        func()
    return inner

@contextmanager
def ordinary():
    print("I am ordinary")



## Input Object to dump function : ordinary

#########################     INPUT ENDS HERE     ##############################


#########################     OUTPUT     ##############################
from contextlib import contextmanager
@contextmanager
def ordinary():
    print("I am ordinary")

#########################     OUTPUT ENDS HERE     ##############################
