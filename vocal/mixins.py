from vocal.netcdf.mixins import (
    DatasetNetCDFMixin,
    GroupNetCDFMixin,
    VariableNetCDFMixin,
    DimensionNetCDFMixin,
)
from vocal.utils.mixins import DatasetUtilsMixin, VocalValidatorsMixin


class VocalDatasetMixin(DatasetNetCDFMixin, DatasetUtilsMixin, VocalValidatorsMixin):
    pass


class VocalVariableMixin(VariableNetCDFMixin, VocalValidatorsMixin):
    pass


class VocalDimensionMixin(DimensionNetCDFMixin, VocalValidatorsMixin):
    pass


class VocalGroupMixin(GroupNetCDFMixin, VocalValidatorsMixin):
    pass


class VocalAttributesMixin(VocalValidatorsMixin):
    pass
