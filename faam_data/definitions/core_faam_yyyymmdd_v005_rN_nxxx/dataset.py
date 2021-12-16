from .variables import variables
from ...dataset import Dataset, DatasetMeta
from ...definitions import global_attribute_factory
from ...definitions.dimensions import Time, sps32

meta = DatasetMeta(
    file_pattern = 'core_faam_[0-9]{8}_v005_r[0-9]+_[a-z][0-9]{3}.nc'
)

dataset = Dataset.construct(
    meta=meta,
    dimensions=[Time, sps32],
    attributes=global_attribute_factory(),
    variables=variables
)