#########################     INPUT     ##############################
def make_pretty(func):
    def inner():
        print("I got decorated")
        func()
    return inner

@make_pretty
def ordinary():
    print("I am ordinary")



## Input Object to dump function : ordinary

#########################     INPUT ENDS HERE     ##############################


#########################     OUTPUT     ##############################


 ## Please check dump function not able to handle above code ## 

#########################     OUTPUT ENDS HERE     ##############################
