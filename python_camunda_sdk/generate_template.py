from python_camunda_sdk import generate_template as p_generate_template
import importlib
from loguru import logger
import click
import re

@click.command()
@click.argument(
    'connector_name',
    help=(
        'Name of connector class including module name, '
        'e.g. mymodule.MyConnector'
    )
)
@click.argument(
    'filename',
    help='Name of the output file'
)
def generate_template(connector_name, filename):
    match = re.search(
        '([a-zA-Z_\.]*)\.([a-zA-Z]*)',
        connector_name
    )

    if match is None:
        raise ValueError('Invalid connector name')

    module_name = match.group(1)
    cls_name = match.group(2)

    module = importlib.import_module(module_name)

    connector_cls = getattr(module, cls_name, None)

    if connector_cls is None:
        raise ValueError(f'Could not import {cls_name} from {module}')

    template = p_generate_template(connector_cls)
    with open(filename, 'w') as f:
        f.write(template.json(exclude_none=True, by_alias=True))

    logger.info(f"Generated template for {connector_name}")


if __name__ == "__main__":
    generate_template()