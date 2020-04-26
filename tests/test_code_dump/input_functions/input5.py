x=20
y=11
def outer_function():
    lambda_func = lambda x: x*x
    output_value=lambda_func(y)
    return output_value

print(outer_function())
