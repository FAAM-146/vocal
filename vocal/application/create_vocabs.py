import sys

from argparse import Namespace

from . import parser_factory

def main():
    parser = parser_factory(
        name='create_vocabs',
        description='Create versioned JSON vocabularies for a vocal project'
    )

    parser.add_argument(
        'project', type=str, metavar='PROJECT',
        help='The path of a vocal project for which to create vocabularies'
    )

    parser.add_argument(
        '-v', type=str, required=True, metavar='VERSION', dest='version',
        help='The vocabulary version, e.g. 1.0'
    )

    
    args = parser.parse_args(sys.argv[2:])