from .variables import variables
from ..dimensions import Time
from ...dataset import Dataset
from ...definitions import global_attribute_factory

dataset = Dataset.construct(
    dimensions=[Time],
    attributes=global_attribute_factory(),
    variables=variables
)