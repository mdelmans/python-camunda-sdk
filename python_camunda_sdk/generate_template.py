from python_camunda_sdk import generate_template as p_generate_template
import importlib
import click
import re
import json

@click.command()
@click.argument(
    'connector',
    type=str
)
@click.argument(
    'filename',
    type=click.Path(writable=True, dir_okay=False)
)
def generate_template(connector, filename):
    '''
    Generates a template from a CONNECTOR and saves it to FILENAME.

    CONNECTOR must be a a full class name including the module name,
    e.g. mymodule.submodule.MyConnector. 
    '''

    if not filename.endswith('.json'):
        raise click.FileError(filename, 'FILENAME must be a .json file')

    match = re.search(
        '([a-zA-Z_\.]*)\.([a-zA-Z]*)',
        connector
    )

    if match is None:
        raise click.BadParameter('Invalid connector name')

    module_name = match.group(1)
    cls_name = match.group(2)
    try:
        module = importlib.import_module(module_name)
    except ModuleNotFoundError:
        raise click.BadParameter(f'Module {module_name} not found') 

    connector_cls = getattr(module, cls_name, None)

    if connector_cls is None:
        raise click.BadParameter(
            f'Could not import {cls_name} from {module_name}'
        )

    template = p_generate_template(connector_cls)
    with open(filename, 'w') as f:
        data = json.dumps(
            template.dict(
                exclude_none=True,
                by_alias=True
            ),
            indent=2
        )
        f.write(data)
    click.echo(f"Generated template for {connector}")


if __name__ == "__main__":
    generate_template()