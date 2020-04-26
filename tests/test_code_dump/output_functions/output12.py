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

## Input Object to dump function : smart_divide

#########################     INPUT ENDS HERE     ##############################


#########################     OUTPUT     ##############################
def smart_divide(func):
   def inner(a,b):
      print("I am going to divide",a,"and",b)
      if b == 0:
         print("Whoops! cannot divide")
         return

      return func(a,b)
   return inner
#########################     OUTPUT ENDS HERE     ##############################
