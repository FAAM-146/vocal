from distutils.core import setup

setup(
    name='vocal',
    version='0.1.0',
    description='FAAM Dataset Management',
    author='Dave Sproson',
    author_email='dave.sproson@faam.ac.uk',
    url='https://github.com/FAAM-146/vocal',
    packages=[
        'vocal', 'vocal.application', 'vocal.types', 'vocal.netcdf',
        'vocal.netcdf.mixins', 'vocal.utils', 'vocal.training',
        'vocal.training.hooks'
    ],
    package_data={
        'vocal': ['py.typed'],
    },
    scripts=['scripts/vocal'],
    install_requires=[
        'netCDF4>=1.6.2',
        'pydantic>=2',
        'pyyaml>=6.0',
        'numpy>=1.24.3',
        'cfunits>=3.3.6'
    ]
)
