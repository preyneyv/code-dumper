# Code Dumper
This library attempts to extract the minimum required amount of code for a given
class/function to run properly.

## Installation
Clone the repository and run the following command in the project root.
```shell script
pip install -e .
```

## Usage
The library provides two helper methods, `pretty_print` and `dump`.
### Using `code_dumper.dump`
`code_dumper.dump()` takes only one argument, which is a reference to the
target function or class.
```python
from code_dumper import dump

global_variable = 3

def unused_func(): pass

def global_func():
    return global_variable

class Test:
    def __init__(self):
        print(global_func())

print(dump(Test))
```
### Using `code_dumper.pretty_print`
`code_dumper.pretty_print()` has one required argument, the object to be
dumped. In addition, it takes four optional arguments.

|  Argument |    Includes    |
|-----------|----------------|
|with_source|source code     |
|with_vars  |found variables |
|with_result|the final result|
|with_logs  |debug logs      |
```python
from code_dumper import pretty_print

global_variable = 3

def unused_func(): pass

def global_func():
    return global_variable

class Test:
    def __init__(self):
        print(global_func())

pretty_print(Test, 
             with_source=True, with_vars=True,
             with_result=True, with_logs=False)
```

## Debugging
You can see debug logs by adding to the top of your file.
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```
Also, if you're using a debugger, adding a breakpoint right before returning
from `CodeDumper.dump()` tends to help, since you can see the final processed
state.
