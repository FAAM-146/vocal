from .constants import (
    ACKNOWLEDGEMENT, CREATOR_ADDRESS, 
    CREATOR_INSTITUTION, KEYWORDS_VOCABULARY, LICENSE, NAMING_AUTHORITY,
    PLATFORM, PLATFORM_TYPE, PUBLISHER_EMAIL, PUBLISHER_INSTITUTION, 
    PUBLISHER_TYPE, PUBLISHER_URL
)

from .schema_types import (DerivedString, DerivedFloat32, DerivedInteger32)

required_globals = {
    'Conventions': 'CF-1.9 ACDD-1.3',
    'acknowledgement': ACKNOWLEDGEMENT,
    'creator_address': CREATOR_ADDRESS,
    'creator_email': DerivedString,
    'creator_institution': CREATOR_INSTITUTION,
    'creator_name': DerivedString,
    'creator_type': 'institution',
    'date': DerivedString,
    'date_created': DerivedString,
    'flight_date': DerivedString,
    'flight_number': DerivedString,
    'geospatial_bounds': DerivedString,
    'geospatial_bounds_crs': 'EPSG:4979',
    'geospatial_lat_min': DerivedFloat32,
    'geospatial_lat_units': 'degree_north',
    'geospatial_lat_max': DerivedFloat32,
    'geospatial_lon_min': DerivedFloat32,
    'geospatial_lon_max': DerivedFloat32, 
    'geospatial_lon_units': 'degree_east',
    'geospatial_vertical_min': DerivedFloat32,
    'geospatial_vertical_max': DerivedFloat32,
    'geospatial_vertical_units': 'm',
    'geospatial_vertical_positive': 'up',
    'id': DerivedString,
    'institution': CREATOR_INSTITUTION,
    'keywords': DerivedString,
    'keywords_vocabulary': KEYWORDS_VOCABULARY,
    'license': LICENSE,
    'metadata_link': DerivedString,
    'naming_authority': NAMING_AUTHORITY,
    'platform': PLATFORM,
    'platform_type': PLATFORM_TYPE,
    'project': DerivedString,
    'publisher_email': PUBLISHER_EMAIL,
    'publisher_institution': PUBLISHER_INSTITUTION,
    'publisher_type': PUBLISHER_TYPE,
    'publisher_url': PUBLISHER_URL,
    'revision_date': DerivedString,
    'revision_number': DerivedInteger32,
    'source': DerivedString,
    'standard_name_vocabulary': DerivedString,
    'summary': DerivedString,
    'time_coverage_duration': DerivedString,
    'time_coverage_start': DerivedString,
    'time_coverage_end': DerivedString,
    'title': DerivedString,
    'uuid': DerivedString,
}

required_variable = {
    '_FillValue': -9999,
    'coverage_content_type': DerivedString,
    'frequency': DerivedInteger32,
    'long_name': DerivedString,
    'units': DerivedString,
}