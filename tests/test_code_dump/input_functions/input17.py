
def adder(y):
    return y+y

def create_adder(x):
    return adder(x)


print(create_adder(2))