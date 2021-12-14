import datetime

from typing import Optional

from pydantic import BaseModel, Field


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