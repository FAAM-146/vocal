from pydantic import BaseModel, root_validator, Field, validator
from typing import  Optional, Union, List, Any
import datetime
from enum import Enum

from uuid import UUID

from .constants import (
    ACKNOWLEDGEMENT, ALLOWED_CALENDARS, AXIS_TYPES, COVERAGE_CONTENT_TYPES, CREATOR_ADDRESS, 
    CREATOR_INSTITUTION, CREATOR_TYPES, KEYWORDS_VOCABULARY, LICENSE, NAMING_AUTHORITY, PLATFORM, PLATFORM_TYPE, PUBLISHER_EMAIL, 
    PUBLISHER_INSTITUTION, PUBLISHER_TYPE, PUBLISHER_URL
)
from .schema_types import (
    DerivedFloat32, DerivedInteger32, DerivedString, DerivedType, Numeric
)

from .validation import (re_validator, is_in_factory, default_value_factory)


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
    actual_range: Optional[List[Numeric]] = Field(description='A length 2 array, of the same datatype as the variable, giving the maximum and minimum valid values', min_items=2, max_items=2)
    add_offset: Optional[Numeric] = Field(description='Offset for packing. Default is 0')
    ancillary_variables: Optional[str] = Field(description='Optional in no ancillary variables, otherwise required. Ancillary variables e.g. flags, uncertainties')
    calendar: Optional[str] = Field(description=f'Required for the time coordinate variable. Should be one of {", ".join(ALLOWED_CALENDARS)}')
    calibration_date: Optional[datetime.date] = Field(description='Calibration date, where this applies to variable')
    calibration_information: Optional[str] = Field(description='Calibration information, where this applies variable')
    calibration_url: Optional[str] = Field(description='Permanent URI or DOI linking to calibration info, where this applies to variable')
    comment: Optional[str] = Field(description='Comment about data')
    coordinates: Optional[str] = Field(description='Blank separated list of coordinate variables')
    flag_masks: Optional[List[Numeric]] = Field(description='Allowed flag mask values. Required for bitmask style flags')
    flag_meanings: Optional[str] = Field(description='Blank separated list of flag meanings. Required for flag variables')
    flag_values: Optional[List[Numeric]] = Field(description='Allowed flag values. Required for classic flags')
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
    valid_range: Optional[List[Numeric]] = Field(description='A length 2 array of the same datatype as the variable, giving minimum and maximum valid values', min_items=2, max_items=2)
    processing_level: Optional[str] = Field(description='Processing level of variable data')





class GroupAttributes(BaseModel):
    class Config:
        title = 'FAAM Group Metadata Schema'
        

    calibration_date: Optional[datetime.date] = Field(description='Calibration date, where this applies to whole group')
    calibration_information: Optional[str] = Field(description='Calibration information, where this applies whole group')
    calibration_url: Optional[str] = Field(description='Permanent URI or DOI linking to calibration info, where this applies to whole group')
    comment: Optional[str] = Field(description='Comment about data')
    instrument: Optional[str] = Field(description='Currently freeform, controlled instrument vocab to follow')
    instrument_description: Optional[str] = Field(description='Textual description.')
    instrument_location: Optional[str] = Field(description='Location of instrument on aircraft')
    instrument_manufacturer: Optional[str] = Field(description='Instrument manufacturer')
    instrument_model: Optional[str] = Field(description='Instrument model')
    instrument_serial_number: Optional[str] = Field(description='Instrument serial number')
    instrument_software: Optional[str] = Field(description='Name of softeare deployed on instrument')
    instrument_software_version: Optional[str] = Field(description='Version of software deployed on instrument')
    notes: Optional[str] = Field(description='Notes on this group. For more detailed info than comment')
    source_files: Optional[str] = Field(description='List of source files used in the processing of this group')
    references: Optional[str] = Field(description=  'A list of references relevant to the group')
    processing_level: Optional[str] = Field(description='Processing level of data, where it is uniform for all data in the group')
    source: Optional[str] = Field(description='A description of the source of the data. An instrument where this makes sense, otherwise a description of how data obtained')
    summary: Optional[str] = Field(description='A brief summary of the data')


        
class GlobalAttributes(BaseModel):
    class Config:
        title = 'FAAM Global Metadata Schema'
   
    Conventions: str = Field(description="The conventions followed by this data", regex='CF-1.9,?\s?ACDD-1.3')
    acknowledgement: str = Field(description=f'The acknowledgement for use of this data. Should read: {ACKNOWLEDGEMENT}')
    creator_address: str = Field(description=f'The address of the FAAM offices. Should read: {CREATOR_ADDRESS}')
    creator_email: str = Field(description='The email address of the data creator, or a generic FAAM email.', regex='.+@.+')
    creator_institution: str = Field(description=f'The institute responsible for the creation of the data. Should read: {CREATOR_INSTITUTION}')
    creator_name: str = Field(description='The name of the person or institute responsible for this data')
    creator_type: str = Field(description=f'The type of creator. Should be one of {", ".join(CREATOR_TYPES)}')
    date: datetime.date = Field(description='Date of the flight')
    date_created: datetime.datetime = Field(description='ISO:8601 date/time file created, ideally yyyy-mm-ddTHH:MM:SSZ. Equivalent to revision_date.')
    flight_date: datetime.date = Field(description='Date of the flight')
    flight_number: str = Field(description='The flight number', regex='[a-z][0-9]{3}')
    geospatial_bounds: str = Field(description='A well-known text representation of the flight envelope')
    geospatial_bounds_crs: str = Field(description='Coordinate reference system for geospatial attributes.', regex='EPSG:[0-9]+')
    geospatial_lat_max: float = Field(ge=-90, le=90, description='Maximum latitude of the flight.')
    geospatial_lat_min: float = Field(ge=-90, le=90, description='Minimum latitude of the flight.')
    geospatial_lat_units: str = Field(description='The units for geospatial_lat_* attributes')
    geospatial_lon_max: float = Field(description='Maximum longitude of the flight', gt=-360, lt=360)
    geospatial_lon_min: float = Field(description='Minimum longitude of the flight', gt=-360, le=360)
    geospatial_vertical_max: float = Field(description='The maximum altitude of the flight')
    geospatial_vertical_min: float = Field(description='The minimum altitude of the flight')
    geospatial_vertical_units: str = Field(description='Vertical units associated with geospatial_vertical_* attributes')
    geospatial_vertical_positive: str = Field(description='Positive direction of geospatial_vertical_* attributes')
    id: str = Field(description='filename without extension, needs to be globally unique w/ naming_authority')
    institution: str = Field(description=f'The institute responsible for the creation of this data. Should read: {CREATOR_INSTITUTION}')
    keywords: str = Field(description='A comma separated list of keywords from the GCMD')
    keywords_vocabulary: str = Field(description=f'Controlled vocabulary for keywords. Should read {KEYWORDS_VOCABULARY}')
    license: str = Field(description=f'The license for this data. Should read: {LICENSE}')
    metadata_link: str = Field(description='A link to a release of a controlled vocabulary of metadata attributes')
    naming_authority: str = Field(description=f'The authority responsible for naming this data. Should read {NAMING_AUTHORITY}')
    platform: str = Field(description=f'Platform name of the FAAM aircraft. Should read: {PLATFORM}')
    platform_type: str = Field(description='Platform type: aircraft')
    project: str = Field(description='The project a flight was for. Expected to be of the form <project_acronym> - <project_name>')
    publisher_email: str = Field(description='The email address of the data publisher', regex='.+@.+')
    publisher_institution: str = Field(description=f'The institution responsible for publishing data. Should read: {PUBLISHER_INSTITUTION}')
    publisher_type: str = Field(description=f'Type of entity responsible for publishing data. Should be {PUBLISHER_TYPE}')
    publisher_url: str = Field(description=f'The URL of the data publisher. Should be {PUBLISHER_URL}')
    references: str = Field(description='A list of references relevant to the file')
    revision_date: datetime.datetime = Field(description='The date this revision created. Analogous to date_created')
    revision_number: int = Field(description='The revision number of the dataset. Starts at 0, increments by 1 for each revision', ge=0)
    source: str = Field(description='A description of the source of the data. An instrument where this makes sense, otherwise a description of how data obtained')
    standard_name_vocabulary: str = Field(description='A vocabulary of standard names. Expected to be a CF standard name table, e.g. CF Standard Name Table v78', regex='CF Standard Name Table v[0-9]+')
    summary: str = Field(description='A brief summary of the data')
    time_coverage_duration: datetime.timedelta = Field(description='The duration of the data, in ISO8601 duration format')
    time_coverage_start: datetime.datetime = Field(description='The start time of the data in the file, in ISO8601 format')
    time_coverage_end: datetime.datetime = Field(description='The end time of the data in the file, in ISO8601 format')
    title: str = Field(description='A brief title for the dataset')
    uuid: UUID = Field(description='V3 UUID: MD5 hash of id+date_created e.g. 9bceaff5-9991-85c6-bca5-d8c0393dc60d')

    # Optional Globals
    calibration_date: Optional[datetime.date] = Field(description='Calibration date, where this applies to all file contents')
    calibration_information: Optional[str] = Field(description='Calibration information, where this applies all file contents')
    calibration_url: Optional[str] = Field(description='Permanent URI or DOI linking to calibration info, where this applies to all file contents')
    comment: Optional[str] = Field(description='Comment about data')
    constants_file: Optional[str] = Field(description='Name of external file providing input to processing software')
    creator_url: Optional[str] = Field(description='Institutional URL or researcher ORCID URL')
    deployment_mode: Optional[str] = Field(description='Mode of deployment. Should always be "air"')
    external_variables: Optional[str] = Field(description='Blank separated list of variables used from an external file')
    history: Optional[str] = Field(description='Logs modifications to file since production')
    instrument: Optional[str] = Field(description='Where all data id from a single instrument. Currently freeform, controlled instrument vocab to follow')
    instrument_description: Optional[str] = Field(description='Where all data are from a single instrument. Textual description.')
    instrument_location: Optional[str] = Field(description='Where all data are from a single instrument. Location of instrument on aircraft')
    instrument_manufacturer: Optional[str] = Field(description='Where all data are from a single instrument. Instrument manufacturer')
    instrument_model: Optional[str] = Field(description='Where all data are from a single instrument. Instrument model')
    instrument_serial_number: Optional[str] = Field(description='Where all data are from a single instrument. Instrument serial number')
    instrument_software: Optional[str] = Field(description='Where all data are from a single instrument. Name of software deployed on instrument')
    instrument_software_version: Optional[str] = Field(description='Where all data are from a single instrument. Version of software deployed on instrument')
    notes: Optional[str] = Field(description='Notes on this data file. For more detailed info than comment')
    processing_software_commit: Optional[str] = Field(description='Commit hash for processing software in vcs')
    processing_software_doi: Optional[str] = Field(description='DOI of the processing doftware release, if available')
    processing_software_url: Optional[str] = Field(description='URL pointing to processing software source code, if available')
    processing_software_version: Optional[str] = Field(description='Version of processing software')
    project_acronym: Optional[str] = Field(description='Project acronym')
    project_name: Optional[str] = Field(description='Full project name')
    project_principal_investigator: Optional[str] = Field(description='Name(s) of project PIs. Comma separated if more than one')
    project_principal_investigator_email: Optional[str] = Field(description='Email address(es) of project PIs. Comma separated if more than one')
    project_princpial_investigator_url: Optional[str] = Field(description='ORCID URL(s) of project PIs. Comma separated if more than one')
    revision_comment: Optional[str] = Field(description='Brief description of changes between revisions')
    source_files: Optional[str] = Field(description='List of source files used in the processing of this data product')
    time_coverage_resolution: Optional[str] = Field(description='Resolution of data, where this is uniform across the file')
    processing_level: Optional[str] = Field(description='Processing level of data, where it is uniform for all data in the file')


    _validate_acknowledgement = re_validator('acknowledgement')(default_value_factory(ACKNOWLEDGEMENT))
    _validate_creator_address = re_validator('creator_address')(default_value_factory(CREATOR_ADDRESS))
    _validate_creator_institution = re_validator('creator_institution')(default_value_factory(CREATOR_INSTITUTION))
    _validate_creator_type = re_validator('creator_type')(is_in_factory(CREATOR_TYPES))
    _validate_geospatial_vertical_units = re_validator('geospatial_vertical_units')(default_value_factory('m'))
    _validate_geospatial_vertical_positive = re_validator('geospatial_vertical_positive')(default_value_factory('up'))
    _validate_keywords_vocabulary = re_validator('keywords_vocabulary')(default_value_factory(KEYWORDS_VOCABULARY))
    _validate_license = re_validator('license')(default_value_factory(LICENSE))
    _validate_naming_authority = re_validator('naming_authority')(default_value_factory(NAMING_AUTHORITY))
    _validate_platform = re_validator('platform')(default_value_factory(PLATFORM))
    _validate_publisher_type = re_validator('publisher_type')(default_value_factory(PUBLISHER_TYPE))
    _validate_publisher_institution = re_validator('publisher_institution')(default_value_factory(PUBLISHER_INSTITUTION))
    _validate_publisher_url = re_validator('publisher_url')(default_value_factory(PUBLISHER_URL))


    @root_validator
    @classmethod
    def root_validate(cls, values):
        if values.get('geospatial_lat_min') > values.get('geospatial_lat_max'):
            raise ValueError('lat min > lat_max')

        return values