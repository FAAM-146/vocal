from dataclasses import dataclass, field
import enum
from typing import Any, Iterable, Optional, Union
from vocal.netcdf import NetCDFReader
from vocal.types import UnknownDataType, type_from_spec, np_invert

import json
import re

PLACEHOLDER_RE = ('<(?P<container>Array)?'
                  '\[?(?P<dtype>[a-z0-9]+)\]?'
                  ': derived_from_file'
                  '\s?'
                  '(?P<additional>.*)>')


class VariableStatus(enum.Enum):
    EXISTS = enum.auto()
    DOES_NOT_EXIST_AND_REQUIRED = enum.auto()
    DOES_NOT_EXIST_AND_NOT_REQUIRED = enum.auto()


@dataclass
class AttributeProperties:
    optional: bool = False
    regex: Optional[str] = None


class CheckException(Exception):
    """
    An exception which may be raised by a CheckError
    """


class NotCheckedError(Exception):
    """
    An exception which may be raised when check properties are 
    accessed before checks have been carried out
    """


class ElementDoesNotExist(Exception):
    """
    Raised when an non existant variable is requested by name
    """


class InvalidPlaceholder(Exception):
    """
    Raised when an invalid placeholder is used in a check
    """


@dataclass
class CheckError:
    """
    Represents an error in a check
    """
    message: str
    path: str

    def raise_err(self) -> None:
        raise CheckException(self.message)


@dataclass
class CheckWarning:
    """
    Represents a warning in a check
    """
    message: str
    path: str


@dataclass
class CheckComment:
    """
    Represents a comment in a check
    """
    message: str
    path: str


@dataclass
class Check:
    """
    Represents a single check
    """
    description: str
    passed: bool = True
    has_warning: bool = False
    has_comment: bool = False
    error: Union[CheckError, None] = None
    warning: Union[CheckWarning, None] = None
    comment: Union[CheckComment, None] = None


@dataclass
class DimensionCollector:
    
    dimensions: list[dict] = field(default_factory=list)

    def search(self, container: dict, depth: int=99) -> list[dict]:

        if depth == 0:
            return self.dimensions

        for dim in container.get('dimensions', []):
            self.dimensions.append(dim)

        for group in container.get('groups', []):
            self.search(group, depth=depth-1)
        

        return self.dimensions


@dataclass
class ProductChecker:
    """
    A class providing methods to check a file against a product definition
    """

    definition: str

    def __post_init__(self) -> None:
        self.checks: list[Check] = []
        self._passing: Union[bool, None] = None

    @property
    def passing(self) -> bool:
        """
        Returns True if all checks have passed, False if any have failed, or
        raises a NotCheckedError if no checks have been carried out
        """
        if not self.checks:
            raise NotCheckedError('Checks have not been performed')

        return all([i.passed for i in self.checks])

    @property
    def warnings(self) -> list[CheckWarning]:
        """
        Returns a list of CheckWarnings for checks which have warning on them, or
        raises a NotCheckedError if no checks have been carried out
        """
        if not self.checks:
            raise NotCheckedError('Checks have not been performed')

        return [i.warning for i in self.checks if i.has_warning and i.warning]

    @property
    def errors(self) -> list[CheckError]:
        """
        Returns a list of CheckErrors for failed checks. Raises a NotCheckedError
        if no checks have been carried out.
        """
        if not self.checks:
            raise NotCheckedError('Checks have not been performed')

        return [i.error for i in self.checks if not i.passed]  # type: ignore
    
    @property
    def comments(self) -> list[CheckComment]:
        """
        Returns a list of CheckComments for checks which have comments on them, or
        raises a NotCheckedError if no checks have been carried out
        """
        if not self.checks:
            raise NotCheckedError('Checks have not been performed')
        
        return [i.comment for i in self.checks if i.has_comment and i.comment]


    def _check(self, description:str, passed: bool=True, error: Optional[CheckError] = None) -> Check:
        """
        Creates and returns a new Check.

        Args:
            description: A description of the check

        Kwargs:
            passed: True if the check has passed, False otherwise. True at init.
            error: CheckError, required if initializing a failed check.

        Returns:
            A new Check
        """
        check = Check(description=description, passed=passed, error=error)
        self.checks.append(check)
        return check

    def get_type_from_placeholder(self, placeholder: str) -> tuple[str, str]:
        """
        Returns the type from a placeholder string. 

        Args:
            placeholder: the placeholder string

        Returns:
            An info type, for example <str>, <float32>
        """
        
        rex = re.compile(PLACEHOLDER_RE)
        matches = rex.search(placeholder)
        if not matches:
            raise ValueError('Unable to get type from placeholder')

        dtype = f'<{matches["dtype"]}>'
        container = matches['container']

        return dtype, container

    def get_attribute_props_from_placeholder(self, placeholder: str) -> AttributeProperties:
        """
        Returns additional attributes from a placeholder string.

        Args:
            placeholder: the placeholder string

        Returns:
            Additional placeholder info, in the form of an AttributeProperties object.
        """

        rex = re.compile(PLACEHOLDER_RE)
        matches = rex.search(placeholder)
        if matches is None:
            raise InvalidPlaceholder(f'Invalid placeholder: {placeholder}')

        additional = matches['additional']
        additional_rex = re.compile(
            '(?P<optional>optional)?,'
            '?((regex=)(?P<regex>.+))?'
        )
        matches = additional_rex.search(additional)
        if matches is None:
            raise InvalidPlaceholder(f'Invalid placeholder: {placeholder}')
        
        optional = matches['optional'] == 'optional'
        regex =  matches['regex']
        
        return AttributeProperties(optional=optional, regex=regex)

    def check_attribute_type(self, d: Any, f: Any, path: str='') -> None:
        """
        Checks the type of an attribute is correct, given a placeholder string
        in the product definition file.

        Args:
            d: the attribute in the product definition
            f: the attribute in the netcdf file

        Kwargs:
            path: full path of the attribute in the netCDF

        Returns:
            None
        """

        check = self._check(
            description=f'Checking attribute {path} type is correct'
        )

        expected_type, container = self.get_type_from_placeholder(d)
        actual_type = np_invert[type(f)]

        if expected_type == actual_type:
            return

        if container == 'Array' and actual_type is list:
            if all([np_invert[type(i)] == expected_type for i in f]):
                return

        if actual_type is list:
            actual_type = [np_invert[type(i)] for i in f]
        check.passed = False
        check.error = CheckError(
            message=f'Type of {path} incorrect. Expected {expected_type}, got {actual_type}',
            path=path
        )
        

    def check_attribute_value(self, d: Any, f: Any, path: str='') -> None:
        """
        Checks the value of an attribute, where it is specified in the 
        product definition.

        Args:
            d: the attribute in the product definition
            f: the attribute in the netcdf file

        Kwargs:
            path: full path of the attribute in the netCDF

        Returns:
            None
        """

        # If the attribute is a placeholder, all we can do is check the type
        if isinstance(d, str) and 'derived_from_file' in d:
            return self.check_attribute_type(d, f, path=path)

        # If the attribute is a list, we need to check each element
        if isinstance(d, list):
            if len(d) > 1:
                for i, (_d, _f) in enumerate(zip(d, f)):
                    self.check_attribute_value(_d, _f, path=f'{path}[{i}]')
                return
            d = d[0]
        
        if d == f:
            return

        check = self._check(
            description=f'Checking value of {path}'
        )

        check.passed = False
        check.error = CheckError(
            message=f'Unexpected value of {path}. Got [{f}], expected: [{d}]',
            path=path
        )

    def compare_attributes(self, d: dict, f: dict, path: str='') -> None:
        """
        Compare the attributes in a netCDF container against the product 
        definition

        Args:
            d: a dict representation of the container from the specification
            f: a dict representation of the container from the netcdf file

        Kwargs:
            path: the pull path of the container

        Returns:
            None
        """
        if not path:
            path = '/'

        for def_key, def_value in d.items():
            check = self._check(
                description=f'Checking attribute {path}.{def_key} exists'
            )

            if def_key not in f:
                if isinstance(def_value, str) and def_value.startswith('<'):
                    attr_props = self.get_attribute_props_from_placeholder(def_value)
                    if attr_props.optional:
                        continue
                else:
                    check.passed = False
                    check.error = CheckError(
                        message=f'Attribute .{def_key} not in {path}',
                        path=f'{path}.{def_key}'
                    )

                check.passed = False
                check.error = CheckError(
                    message=f'Attribute .{def_key} not in {path}',
                    path=f'{path}.{def_key}'
                )
                continue
            
            self.check_attribute_value(d[def_key], f[def_key], path=f'{path}.{def_key}')

        for file_key in f:
            check = self._check(
                description=f'Checking attribute {path}.{file_key} in definition'        
            )
            if file_key not in d:
                check.has_warning = True
                check.warning = CheckWarning(
                    message=f'Found attribute .{file_key} which is not in definition',
                    path=f'{path}.{file_key}'
                )


    def get_element(self, name: str, container: Iterable) -> dict:
        """
        Return an element from an iterable container, using the 
        name element of the container meta.

        Args:
            name: the name (variable/group) to find
            container: an iterable yielding variables or groups

        Returns:
            a dict representation of the requested variable.

        Raises:
            ElementDoesNotExist if the variable is not found in the parent
        """
        for i in container:
            if i['meta']['name'] == name:
                return i
        
        raise ElementDoesNotExist(f'Element {name} not found')

    def check_variable_exists(
        self, name: str, parent: Iterable, path: str='', from_file: bool=False,
        required: bool=True
        ) -> VariableStatus:
        """
        Check a variable exists in a parent, which is assumed to be an iterable
        yielding a dict representation of the variable.

        Args:
            name: the name of the variable to check
            container: an iterable yielding dict variable representations
            from_file: if True, checking variable from file is in definition,
                       if False, checking variable from definition is in file.
            
        Kwargs:
            path: the full path of the variable in the netCDF

        Returns:
            A VariableStatus enum value
        """

        in_type = 'in definition' if from_file else 'in file'

        check = self._check(description=f'Checking variable {path} exists {in_type}')

        try:
            self.get_element(name, parent)
        except ElementDoesNotExist:
            if not required:
               return VariableStatus.DOES_NOT_EXIST_AND_NOT_REQUIRED
            check.passed = False
            check.error = CheckError(f'Variable does not exist {in_type}', path)
            return VariableStatus.DOES_NOT_EXIST_AND_REQUIRED

        return VariableStatus.EXISTS

    def check_variable_dtype(self, d: dict, f: dict, path: str='') -> None:
        """
        Check the datatype of a variable matches that given in the product
        definition

        Args:
            d: a dict representation of the variable from the specification
            f: a dict representation of the variable from the nerCDF

        Kwargs:
            path: the full path to the variable in the netCDF

        Returns:
            None
        """

        check = self._check(
            description=f'Checking datatype of {path}'
        )
        
        expected_type_str = d['meta']['datatype']
        actual_type_str = f['meta']['datatype']

        actual_dtype = type_from_spec(actual_type_str)

        # Check that the expected datatype is known to vocal
        try:
            expected_dtype = type_from_spec(expected_type_str)
        except UnknownDataType:
            check.passed = False
            check.error = CheckError(
                f'Unknown datatype in specification: {expected_type_str}',
                path
            )
            return


        if actual_dtype != expected_dtype:
            check.passed = False
            check.error = CheckError(
                f'Incorrect datatype. Found {actual_dtype}, expected {expected_dtype}',
                path
            )

        if actual_type_str != expected_type_str:
            check.has_comment = True
            check.comment = CheckComment(
                (f'Found datatype {actual_type_str}. Specification denotes expected '
                 f'datatype as {expected_type_str}, but these are considered equivalent.'),
                path
            )

    def compare_variables(self, d: dict, f: dict, path: str='') -> None:
        """
        Compare all of the variables in a container to those in a product
        specification.

        Args:
            d: a dict representation of the container from the specification
            f: a dict representation of the container from the netcdf file

        Kwargs:
            path: the full path to the container in the netcdf file

        Returns:
            None
        """

        for d_var in d:
            var_name = d_var["meta"]["name"]
            var_required = d_var['meta'].get('required', True)
            var_path = f'{path}/{var_name}'

            variable_stat = self.check_variable_exists(
                var_name, f, path=var_path, required=var_required
            )
            
            if variable_stat in (
                    VariableStatus.DOES_NOT_EXIST_AND_REQUIRED,
                    VariableStatus.DOES_NOT_EXIST_AND_NOT_REQUIRED):
                continue

            f_var = self.get_element(var_name, f)
            self.check_variable_dtype(d_var, f_var, path=var_path)

            self.compare_attributes(d_var['attributes'], f_var['attributes'], path=var_path)

        for f_var in f:
            var_name = f_var["meta"]["name"]
            var_path = f'{path}/{var_name}'

            if not self.check_variable_exists(var_name, d, path=var_path, from_file=True):
                continue

    def compare_groups(self, d: Iterable, f: Iterable, path: str='') -> None:
        """
        Compare the dict representation of groups from a product specification
        and from file

        Args:
            d: The group representation from the specification
            f: The group representation from file

        Kwargs:
            path: The path to the group container

        Returns:
            None
        """

        for def_group in d:
            group_name = def_group["meta"]["name"]
            group_path = f'{path}/{group_name}'
            
            check = self._check(
                description=f'Checking group {group_path} exists'
            )

            try:
                f_group = self.get_element(group_name, f)
            
            except ElementDoesNotExist:
                check.passed = False
                check.error = CheckError(
                    message=f'group not found: {group_path}',
                    path=group_path
                )
                
                continue
            
            self.compare_container(def_group, f_group, path=group_path)

    def compare_dimensions(self, d: dict, f: dict, path: str='') -> None:
        """
        Compare the dict representation of dimensions from a product
        specification and from file.

        We use the DimensionCollector to find the dimensions in the file up
        to the depth of the current path.

        Args:
            d: The dimension representation from the specification
            f: The dimension representation from file

        Kwargs:
            path: The path to the dimension container

        Returns:
            None
        """
        depth = path.count('/') + 1
        def_dims = DimensionCollector().search(d, depth=depth)
        file_dims = DimensionCollector().search(f, depth=depth)

        for dim in file_dims:
            _path = f'{path}/[{dim["name"]}]'
            check = self._check(
                description=f'Checking dimension {dim["name"]} is in definition'
            )

            # The dimension is in the definition. Checking equality here, which
            # encompasses both size and name.
            if dim in def_dims:
                continue

            # The dimension is not in the definition. Checking if there is a
            # dimension with the same name, but different size.
            dims_with_name = [d for d in def_dims if d['name'] == dim['name']]
            if dims_with_name:
                # There is a dimension with the same name, but different size.
                message = (f'Dimension {dim["name"]} found in definition, but '
                           f'with different size. Size in file: {dim["size"]}, '
                           f'size in definition: {dims_with_name[0]["size"]}')
            else:
                # There is no dimension with the same name.
                message = f'Dimension {dim["name"]} not found in definition'
            
            check.passed = False
            check.error = CheckError(
                message=message,
                path=_path
            )

        for dim in def_dims:
            _path = f'{path}/[{dim["name"]}]'
            check = self._check(
                description=f'Checking dimension {dim["name"]} is in file'
            )
            if dim in file_dims:
                continue

            # The dimension is not in the definition. Checking if there is a
            # dimension with the same name, but different size.
            dims_with_name = [d for d in file_dims if d['name'] == dim['name']]
            if dims_with_name:
                # There is a dimension with the same name, but different size.
                message = (f'Dimension {dim["name"]} found in file, but '
                           f'with different size. Size in definition: {dim["size"]}, '
                           f'size in file: {dims_with_name[0]["size"]}')
                check.passed = False
                check.error = CheckError(
                    message=message,
                    path=_path
                )
            else:
                # There is no dimension with the same name.
                message = f'Dimension {dim["name"]} not found in file'

                check.has_warning = True
                check.warning = CheckWarning(
                    message=message,
                    path=_path
                )

    def compare_container(self, d: dict, f: dict, path: str='') -> None:
        """
        Compare the dict representation of a netcdf container from a product
        specification and from file

        Args:
            d: The container representation from a product specification
            f: The container representation from file

        Kwargs:
            path: the path of the container in the netcdf file
        """

        self.compare_dimensions(d, f, path=path)

        self.compare_attributes(d.get('attributes', {}), f.get('attributes', {}), path=path)
        self.compare_variables(d.get('variables', []), f.get('variables', []), path=path)
        self.compare_groups(d.get('groups', []), f.get('groups', []), path=path)

    def load_definition(self) -> dict:
        """
        Load the product definition, and return it as a dict.
        """
        with open(self.definition, 'r') as f:
            product_def = json.load(f)
        return product_def

    def check(self, target_file: str) -> None:
        """
        Check a target file againt the instances product specification

        Args:
            target_file: the path of the file to check
        """
        
        product_def = self.load_definition()
        netcdf_rep = NetCDFReader(target_file).dict

        self.compare_container(product_def, netcdf_rep)