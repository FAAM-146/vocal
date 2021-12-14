from .variables import variables
from ...dataset import Dataset
from ...definitions import global_attribute_factory
from ...definitions.dimensions import Time, sps32

dataset = Dataset.construct(
    dimensions=[Time, sps32],
    attributes=global_attribute_factory(),
    variables=variables
)