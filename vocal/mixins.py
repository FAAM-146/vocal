from vocal.netcdf.mixins import (
    DatasetNetCDFMixin, GroupNetCDFMixin, VariableNetCDFMixin, DimensionNetCDFMixin
)
from vocal.utils.mixins import DatasetUtilsMixin


class VocalDatasetMixin(DatasetNetCDFMixin, DatasetUtilsMixin):
    pass


class VocalVariableMixin(VariableNetCDFMixin):
    pass


class VocalDimensionMixin(DimensionNetCDFMixin):
    pass


class VocalGroupMixin(GroupNetCDFMixin):
    pass