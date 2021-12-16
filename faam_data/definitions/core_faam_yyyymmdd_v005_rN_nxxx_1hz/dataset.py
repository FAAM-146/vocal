from .variables import variables
from ..dimensions import Time
from ...dataset import Dataset, DatasetMeta
from ...definitions import global_attribute_factory


meta = DatasetMeta(
    file_pattern = 'core_faam_[0-9]{8}_v005_r[0-9]+_[a-z][0-9]{3}.nc'

)

dataset = Dataset.construct(
    meta=meta,
    dimensions=[Time],
    attributes=global_attribute_factory(),
    variables=variables
)