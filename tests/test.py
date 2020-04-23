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


@inputs.atomic.generic('asd')
@outputs.atomic.generic('df')
class AddBlock(Block):
    def run(self, asd, df):
        return df.put(asd)

pretty_print(AddBlock, with_source=0, with_logs=1)
