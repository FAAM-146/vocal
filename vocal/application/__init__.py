import argparse
import os

commands = [
    i[:-3] for i in os.listdir(os.path.dirname(__file__))
    if not i.startswith('_')
]

def parser_factory(name, description=None):
    return argparse.ArgumentParser(
        prog='vocal',
        usage=f'%(prog)s {name} [options]',
        description=description
    )