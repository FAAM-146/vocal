import argparse
import os

commands = [
    i[:-3] for i in os.listdir(os.path.dirname(__file__))
    if not i.startswith('_')
]

def parser_factory(file: str, description: str='') -> argparse.ArgumentParser:
    name = '.'.join(os.path.basename(file).split('.')[:-1])
    return argparse.ArgumentParser(
        prog='vocal',
        usage=f'%(prog)s {name} [options]',
        description=description
    )