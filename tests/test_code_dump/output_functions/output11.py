#########################     INPUT     ##############################
def smart_divide(func):
   def inner(a,b):
      print("I am going to divide",a,"and",b)
      if b == 0:
         print("Whoops! cannot divide")
         return

      return func(a,b)
   return inner

@smart_divide
def divide(a,b):
    return a/b

x=divide(2,3)
print(x)

## Input Object to dump function : divide

#########################     INPUT ENDS HERE     ##############################


#########################     OUTPUT     ##############################


 ## Please check dump function not able to handle above code ## 

#########################     OUTPUT ENDS HERE     ##############################
