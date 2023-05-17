# Vocal

Vocal is a tool for managing netCDF data product standards and associated data product specifications.
It is intended to be used with datasets following the [Climate-Forecast Conventions](https://cfconventions.org/),
but may also be used non cf-compliant datasets.

## Installation

The recommended way to install *vocal* is by using the [conda](https://conda.io) environment manager.
These instructions are intended for the linux command line, but may work in other operating system
environments. YMMV.

### Directly with conda

To install *vocal* directly with conda you simply need to obtain the 
[environment file](https://raw.githubusercontent.com/FAAM-146/vocal/main/environment.yml) and run
`conda env create` from the same directory. This installs the non-python dependences with conda
and uses the pip package manager to install *vocal* and its dependencies.

Once the environment has been created, it can be activate with the command `conda activate vocal`.
This should result in the `vocal` script being available in your `PATH`:

    $ vocal
    
    Available commands are:

    * check           - Check a netCDF file against standard and product definitions.
    * create_vocabs   - Create versioned JSON vocabularies for a vocal project
    * eg_data         - Create an example data file from a definition.
    * init            - Initialise a vocal project.

    try "vocal <command> -h" for help

### With conda via git clone (recommended)

Alternatively, it is possible to obtain the conda environment by cloning the *vocal* git 
repository:

    $ git clone git@github.com:FAAM-146/vocal.git
    
    Cloning into 'vocal'...
    <...>
    
    $ cd vocal
    $ conda env create

The conda environment can then be activated as above, providing the `vocal` script.

### With pip

Vocal can also be installed with pip, though in this instance you are responsible for ensuring
that the required [udunits2](https://www.unidata.ucar.edu/software/udunits/) library is available
on your system.

    pip install git+https://github.com/FAAM-146/vocal.git
    
Note that if using pip directly, it is **strongly** recommended that you use a python environment
manager such as [Virtualenv](https://pypi.org/project/virtualenv/).

## Vocal projects

*Vocal* uses vocal projects to define standards for netCDF data. *Vocal* projects are comprised of 
[pydantic](https://docs.pydantic.dev/) model definitions, and associated validators. *Vocal*
then provides a mapping from netCDF data to these models, allowing the power of pydantic to
be used for compliance checking.

Typically as a data provider you will be provided with a *vocal* project to use to check your
data for compliance.

### Creating a new vocal project

To create a new *vocal* project, simply type `vocal init -d <project_name>`. This will create a
directory named `project_name` with the following structure:

    ./models
    ./models/dimension.py
    ./models/group.py
    ./models/dataset.py
    ./models/__init__.py
    ./models/variable.py
    ./attributes
    ./attributes/variable_attributes.py
    ./attributes/global_attributes.py
    ./attributes/group_attributes.py
    ./attributes/__init__.py
    ./definitions
    ./defaults.py
