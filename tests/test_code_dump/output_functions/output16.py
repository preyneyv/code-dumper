#########################     INPUT     ##############################
def shout(text):
    return text.upper()


def whisper(text):
    return text.lower()


def greet(func):
    # storing the function in a variable
    greeting = func("Hi, I am created by a function passed as an argument.")

print(greet(shout))
print(greet(whisper))

## Input Object to dump function : greet

#########################     INPUT ENDS HERE     ##############################


#########################     OUTPUT     ##############################
def greet(func):
    # storing the function in a variable
    greeting = func("Hi, I am created by a function passed as an argument.")
#########################     OUTPUT ENDS HERE     ##############################
