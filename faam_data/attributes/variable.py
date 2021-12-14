import datetime

from typing import Optional, Union


from pydantic import BaseModel, Field

from ..constants import (
    COVERAGE_CONTENT_TYPES, AXIS_TYPES, ALLOWED_CALENDARS
)

from ..schema_types import Numeric

class VariableAttributes(BaseModel):
    class Config:
        title = 'FAAM Variable Metadata Schema'
        fields = {'FillValue': '_FillValue'}

    FillValue: Union[int, float] = Field(description='The prefill/missing data value')
    coverage_content_type: str = Field(description=f'ISO 19115-1 code. One of {", ".join(COVERAGE_CONTENT_TYPES)}')
    frequency: int = Field(description='The frequency of the data. Where this is >1, will typically correspond to an spsNN dimension')
    long_name: str = Field(description='A longer, descriptive name for the variable')
    units: str = Field(description='Valid UDUNITS unit. Where a standard_name is given, must be equivalent to canonical units')

    # Optional Attributes
    axis: Optional[str] = Field(description=f'Axis for coordinate variables. Should be one of {", ".join(AXIS_TYPES)}')
    actual_range: Optional[list[Numeric]] = Field(description='A length 2 array, of the same datatype as the variable, giving the maximum and minimum valid values', min_items=2, max_items=2)
    add_offset: Optional[Numeric] = Field(description='Offset for packing. Default is 0')
    ancillary_variables: Optional[str] = Field(description='Optional in no ancillary variables, otherwise required. Ancillary variables e.g. flags, uncertainties')
    calendar: Optional[str] = Field(description=f'Required for the time coordinate variable. Should be one of {", ".join(ALLOWED_CALENDARS)}')
    calibration_date: Optional[datetime.date] = Field(description='Calibration date, where this applies to variable')
    calibration_information: Optional[str] = Field(description='Calibration information, where this applies variable')
    calibration_url: Optional[str] = Field(description='Permanent URI or DOI linking to calibration info, where this applies to variable')
    comment: Optional[str] = Field(description='Comment about data')
    coordinates: Optional[str] = Field(description='Blank separated list of coordinate variables')
    flag_masks: Optional[list[Numeric]] = Field(description='Allowed flag mask values. Required for bitmask style flags')
    flag_meanings: Optional[str] = Field(description='Blank separated list of flag meanings. Required for flag variables')
    flag_values: Optional[list[Numeric]] = Field(description='Allowed flag values. Required for classic flags')
    instrument_description: Optional[str] = Field(description='Textual description of instrument.')
    instrument_location: Optional[str] = Field(description='Where all data in the group are from a single instrument. Location of instrument on aircraft')
    instrument_manufacturer: Optional[str] = Field(description='Where all data in the group are from a single instrument. Instrument manufacturer')
    instrument_model: Optional[str] = Field(description='Where all data in the group are from a single instrument. Instrument model number')
    instrument_serial_number: Optional[str] = Field(description='Where all data in the group are from a single instrument. Instrument serial number')
    instrument_software: Optional[str] = Field(description='Where all data in the group are from a single instrument. Name of softeare deploed on instrument')
    instrument_software_version: Optional[str] = Field(description='Where all data in the group are from a single instrument. Version of software deployed on instrument')
    positive: Optional[str] = Field(description='Applies to vertical coordinate. Should be "up" if included')
    scale_factor: Optional[Numeric] = Field(description='Scale for packing. Default is 1')
    standard_name: Optional[str] = Field(description='See CF standard names list. Should be used whenever possible')
    valid_max: Optional[Numeric] = Field(description='Recommended where feasible. Where both valid_min and valid_max make sense, valid_range is preferred.')
    valid_min: Optional[Numeric] = Field(description='Recommended where feasible. Where both valid_min and valid_max make sense, valid_range is preferred.')
    valid_range: Optional[list[Numeric]] = Field(description='A length 2 array of the same datatype as the variable, giving minimum and maximum valid values', min_items=2, max_items=2)
    processing_level: Optional[str] = Field(description='Processing level of variable data')