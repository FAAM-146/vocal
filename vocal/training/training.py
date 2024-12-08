import warnings

from dataclasses import dataclass
from functools import partial
from typing import Any, Callable, Union
import netCDF4  # type: ignore

import numpy as np
import numpy.typing
import pydantic

TIME_START = 0
TIME_END = 3601

NT = TIME_END - TIME_START


def geospatial(
    nc: netCDF4.Dataset, axis: str, extrema: str, **kwargs: Any
) -> Union[np.float32, None]:
    """
    Defines a function generic which can be partially completed to provide
    functions which search the netcdf container for coordinate variables and
    selects the min/max values of these.

    Note: this will currently fail if coordinate variables are not in the root
    group.

    Args:
        nc: A netCDF container, assumed to be Dataset
        axis: A string indicating which coordinate axis to use
        extrema: a string, either 'min' or 'max'

    Returns:
        _val: the given extrema over the given axis
    """

    func = getattr(np, extrema)
    extreme_value = -9e99 if extrema == "max" else 9e99

    _val = extreme_value

    for var in nc.variables:
        if getattr(nc[var], "axis", None) != axis:
            continue

        _val = func([func(nc[var][:]), _val])

    if _val == extreme_value:
        _dummy_val = np.float32(0) if extrema == "min" else np.float32(10)
        warnings.warn(
            f"Unable to infer {extrema} geospatial bound on axis {axis}, using {_dummy_val}"
        )
        return _dummy_val

    return np.float32(_val)


# Complete partials for each geospatial attribute
geospatial_lon_max = partial(geospatial, axis="X", extrema="max")
geospatial_lon_min = partial(geospatial, axis="X", extrema="min")
geospatial_lat_max = partial(geospatial, axis="Y", extrema="max")
geospatial_lat_min = partial(geospatial, axis="Y", extrema="min")
geospatial_vertical_max = partial(geospatial, axis="Z", extrema="max")
geospatial_vertical_min = partial(geospatial, axis="Z", extrema="min")


def revision_number(nc: netCDF4.Dataset, attrs: pydantic.BaseModel) -> np.int32:
    revision_number = getattr(attrs, "revision_number", 0)
    return np.int32(revision_number)


def actual_range(
    var: netCDF4.Variable, attrs: pydantic.BaseModel
) -> Union[list[Any], None]:
    try:
        if getattr(attrs, "standard_name", None) == "time":
            return None
    except AttributeError:
        pass

    if getattr(attrs, "flag_meanings", None) is None:
        try:
            return [np.min(var), np.max(var)]
        except (TypeError, ValueError):
            return [var.dtype.type(0), var.dtype.type(0)]
    return None


def units(var: netCDF4.Variable, attrs: pydantic.BaseModel) -> str:
    if getattr(attrs, "standard_name", None) != "time":
        return getattr(attrs, "units")
    return "seconds since 1970-01-01 00:00:00 +0000"


def flag_masks(
    var: netCDF4.Variable, attrs: pydantic.BaseModel
) -> list[np.int8] | None:
    if getattr(attrs, "flag_masks", None) is None:
        return None

    try:
        return [
            np.int8(2**i) for i, _ in enumerate(getattr(attrs, "flag_meanings").split())
        ]
    except (AttributeError, TypeError):
        return None


def flag_values(
    var: netCDF4.Variable, attrs: pydantic.BaseModel
) -> list[np.int8] | None:
    if getattr(attrs, "flag_values", None) is None:
        return None
    try:
        return [
            np.int8(2**i) for i, _ in enumerate(getattr(attrs, "flag_meanings").split())
        ]
    except (AttributeError, TypeError):
        return None


# Hooks for completing variable attributes in test datasets
variable_data_hooks = {
    "actual_range": actual_range,
    "flag_masks": flag_masks,
    "flag_values": flag_values,
    "units": units,
}

# Hooks for completing global attributes in test datasets
global_data_hooks: dict[str, Callable] = {
    "geospatial_lon_max": geospatial_lon_max,
    "geospatial_lon_min": geospatial_lon_min,
    "geospatial_lat_max": geospatial_lat_max,
    "geospatial_lat_min": geospatial_lat_min,
    "geospatial_vertical_max": geospatial_vertical_max,
    "geospatial_vertical_min": geospatial_vertical_min,
    "revision_number": revision_number,
}


@dataclass
class VariableTrainingData:
    """
    A class for populating variables with (meaningless) data for the production
    of training data.
    """

    var: netCDF4.Variable
    attrs: pydantic.BaseModel

    @property
    def freq(self) -> int:
        """
        Shortcut to variable frequency
        """
        return self.attrs.frequency  # type: ignore

    @property
    def axis(self) -> Union[str, None]:
        """
        Shortcut to variable axis, if it's defined
        """
        return getattr(self.attrs, "axis", None)

    def _get_time(self) -> numpy.typing.ArrayLike:
        """
        Get values for a time variable
        """
        time = np.arange(TIME_START, TIME_END)
        return time

    def _get_dummy_data(self) -> numpy.typing.ArrayLike:
        """
        Get dummy sinusoidal data for standard data variables
        """
        size = self._get_data_size()
        scale = np.round(10 * np.random.random())
        x = np.linspace(0, 10 * np.pi, num=int(np.prod(size)))
        return (scale * np.sin(x)).reshape(size).astype(self.var.dtype)

    def _get_dummy_flag(self) -> numpy.typing.ArrayLike:
        """
        Get dummy flag data
        """

        flags = self.attrs.flag_values  # type: ignore

        if flags is None:
            flags = self.attrs.flag_masks  # type: ignore

        if flags is None:
            raise ValueError("Flag variable does not include flag_values or flag_masks")

        try:
            return (flags[0] * np.ones(self._get_data_size())).astype(np.int8)
        except Exception:
            return (0 * np.ones(self._get_data_size())).astype(np.int8)

    def _get_data_size(self) -> tuple:
        sizes = []
        for dim in self.var.get_dims():
            if dim.isunlimited():
                sizes.append(NT)
            else:
                sizes.append(dim.size)

        return tuple(sizes)

    def populate(self) -> None:
        """
        Populate the provided variable with data.
        """

        if getattr(self.attrs, "standard_name", None) == "time":
            self.var[:] = self._get_time()
            return

        if getattr(self.attrs, "flag_meanings", None):
            self.var[:] = self._get_dummy_flag()
            return

        self.var[:] = self._get_dummy_data()
