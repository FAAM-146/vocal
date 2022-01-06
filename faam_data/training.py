from dataclasses import dataclass
from functools import partial
from typing import Union
import netCDF4

import numpy as np
import numpy.typing
import pydantic
from pydantic.types import NoneStr

TIME_START = 0
TIME_END = 3601

NT = TIME_END - TIME_START

def geospatial(nc: netCDF4.Dataset, axis: str, extrema: str) -> Union[float, None]:
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
    extreme_value = -9e99 if extrema == 'max' else 9e99

    _val = extreme_value

    for var in nc.variables:
        if getattr(nc[var], 'axis', None) != axis:
            continue

        _val = func([func(nc[var][:]), _val])

    if _val == extreme_value:
        # This isn't right. geospatial_* attributes are required by the standard.
        # Either raise an error, or fall back on example data
        return None

    return _val

# Complete partials for each geospatial attribute
geospatial_lon_max = partial(geospatial, axis='X', extrema='max')
geospatial_lon_min = partial(geospatial, axis='X', extrema='min')
geospatial_lat_max = partial(geospatial, axis='Y', extrema='max')
geospatial_lat_min = partial(geospatial, axis='Y', extrema='min')
geospatial_vertical_max = partial(geospatial, axis='Z', extrema='max')
geospatial_vertical_min = partial(geospatial, axis='Z', extrema='min')

# Hooks for completing variable attributes in test datasets
variable_data_hooks = {
    'actual_range': lambda x: [np.min(x), np.max(x)]
}

# Hooks for completing global attributes in test datasets
global_data_hooks = {
    'geospatial_lon_max': geospatial_lon_max,
    'geospatial_lon_min': geospatial_lon_min,
    'geospatial_lat_max': geospatial_lat_max,
    'geospatial_lat_min': geospatial_lat_min,
    'geospatial_vertical_max': geospatial_vertical_max,
    'geospatial_vertical_min': geospatial_vertical_min
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
        return self.attrs.frequency

    @property
    def axis(self) -> Union[str, None]:
        """
        Shortcut to variable axis, if it's defined
        """
        return getattr(self.attrs, 'axis', None)

    def _get_time(self) -> numpy.typing.ArrayLike:
        """
        Get values for a time variable
        """
        time = np.arange(TIME_START, TIME_END, 1 / self.freq)
        return time

    def _get_dummy_data(self) -> numpy.typing.ArrayLike:
        """
        Get dummy sinusoidal data for standard data variables
        """
        scale = np.round(10 * np.random.random())
        x = np.linspace(0, 10*np.pi, num=NT*self.freq)
        return (scale * np.sin(x)).reshape((NT, self.freq))

    def _get_dummy_flag(self) -> numpy.typing.ArrayLike:
        """
        Get dummy flag data
        """
        flags = None

        try:
            flags = self.attrs.flag_values
        except AttributeError:
            pass

        try:
            flags = self.attrs.flag_masks
        except AttributeError:
            pass

        if flags is None:
            raise ValueError(
                'Flag variable does not include flag_values or flag_masks'
            )

        return flags[0] * np.ones((NT, self.freq))

    def populate(self) -> None:
        """
        Populate the provided variable with data.
        """
    
        if self.axis == 'T':
            self.var[:] = self._get_time()
            return

        self.var[:] = self._get_dummy_data()