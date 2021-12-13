from faam_data.dataset import Dataset
from faam_data.variable import Variable, VariableMeta
from faam_data.dimension import Dimension
from faam_data.attributes import GlobalAttributes, VariableAttributes
from faam_data.templates import required_globals, required_variable

from faam_data.schema_types import *

from dimensions import *

dataset = Dataset(
    attributes=GlobalAttributes.construct(
        **required_globals
    ),
    variables=[
        Variable(
            meta=VariableMeta.construct(
                shortname='blah',
                datatype=Integer32,
                dimensions=[
                    Time, sps02
                ]
            ),
            attributes=VariableAttributes.construct(**required_variable)
        )
    ]
)



with open('test.json', 'w') as f:
    f.write(Dataset.schema_json())