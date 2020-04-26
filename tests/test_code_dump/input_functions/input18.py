from contextlib import contextmanager
def make_pretty(func):
    def inner():
        print("I got decorated")
        func()
    return inner

@contextmanager
def ordinary():
    print("I am ordinary")

