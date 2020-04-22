from razor.blocks import Block, inputs, outputs
from razor.pipeline import Pipeline
from code_dumper import pretty_print

x = 4
def mult(y):
    return x * y

@inputs.atomic.generic('asdf')
class AddBlock(Block):
    def run(self, asdf):
        return mult(asdf)


pretty_print(AddBlock, with_vars=0, with_source=0, with_logs=1)
