import os
from .. import dataset_from_partial_yaml

dataset = dataset_from_partial_yaml(
    os.path.join(
        os.path.dirname(__file__), 'definition.yaml'
    )
)