from distutils.core import setup

setup(
    name='vocal',
    version='0.1.0',
    description='FAAM Dataset Vocabulary Management',
    author='Dave Sproson',
    author_email='dave.sproson@faam.ac.uk',
    url='https://github.com/FAAM-146/vocal',
    packages=['vocal'],
    scripts=['scripts/vocal_init'],
    install_requires=[
        'netcdf4', 'pydantic', 'pyyaml', 'numpy'
    ]
)