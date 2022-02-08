from dataclasses import dataclass
from typing import Any, Iterable, Optional, Union
from vocal.netcdf import NetCDFReader
from vocal.schema_types import np_invert

import json
import re

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
class Check:
    """
    Represents a single check
    """
    description: str
    passed: bool = True
    has_warning: bool = False
    error: Union[CheckError, None] = None
    warning: Union[CheckWarning, None] = None


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

        return [i.warning for i in self.checks if i.has_warning]

    @property
    def errors(self) -> list[CheckError]:
        """
        Returns a list of CheckErrors for failed checks. Raises a NotCheckedError
        if no checks have been carried out.
        """
        if not self.checks:
            raise NotCheckedError('Checks have not been performed')

        return [i.error for i in self.checks if not i.passed]  # type: ignore


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
        check = Check(description, passed, error)
        self.checks.append(check)
        return check

    def get_type_from_placeholder(self, placeholder: str) -> str:
        """
        Returns the type from a placeholder string. 

        Args:
            placeholder: the placeholder string

        Returns:
            An info type, for example <str>, <float32>
        """
        # rex = re.compile("<([a-z0-9]+): derived_from_file>")
        rex = re.compile('<(Array)?\[?([a-z0-9]+)\]?: derived_from_file>')
        matches = rex.search(placeholder)
        if not matches:
            raise ValueError('Unable to get type from placeholder')

        dtype = f'<{matches.groups()[1]}>'
        container = matches.groups()[0]

        return dtype, container

    def check_attribute_type(self, d: Any, f: Any, path: str='') -> None:
        """
        Checks the type of an attribute is correct, given a placeholder string
        in the product definition file.

        Args:
            d: the attribute in the product definition
            f: the attribute in the netcdf file

        Kwargs:
            path: full path of the attribute in the netCDF
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
        """

        if isinstance(d, str) and 'derived_from_file' in d:
            return self.check_attribute_type(d, f, path=path)

        if isinstance(d, list):
            if len(d) > 1:
                for i, (_d, _f) in enumerate(zip(d, f)):
                    self.check_attribute_value(_d, _f, path=f'{path}[{i}]')
                return
            d = d[0]

        check = self._check(
            description=f'Checking value of {path}'
        )

        if d == f:
            return

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
        """
        if not path:
            path = '/'

        for def_key in d:
            check = self._check(
                description=f'Checking attribute {path}.{def_key} exists'
            )

            if def_key not in f:
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
        self, name: str, parent: Iterable, path: str='', from_file: bool=False
        ) -> bool:
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
            True if the variable exists, False otherwise
        """

        in_type = 'in definition' if from_file else 'in file'

        check = self._check(description=f'Checking variable {path} exists {in_type}')

        try:
            self.get_element(name, parent)
        except ElementDoesNotExist:
            check.passed = False
            check.error = CheckError(f'Variable does not exist {in_type}', path)
            return False

        return True

    def check_variable_dtype(self, d: dict, f: dict, path: str='') -> None:
        """
        Check the datatype of a variable matches that given in the product
        definition

        Args:
            d: a dict representation of the variable from the specification
            f: a dict representation of the variable from the nerCDF

        Kwargs:
            path: the full path to the variable in the netCDF
        """

        expected_dtype = d['meta']['datatype']
        actual_dtype = f['meta']['datatype']
        check = self._check(
            description=f'Checking datatype of {path}'
        )

        if actual_dtype != expected_dtype:
            check.passed = False
            check.error = CheckError(
                f'Incorrect datatype. Found {actual_dtype}, expected {expected_dtype}',
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
        """

        for d_var in d:
            var_name = d_var["meta"]["name"]
            var_path = f'{path}/{var_name}'

            if not self.check_variable_exists(var_name, f, path=var_path):
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

        self.compare_attributes(d['attributes'], f['attributes'], path=path)
        self.compare_variables(d['variables'], f['variables'], path=path)
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