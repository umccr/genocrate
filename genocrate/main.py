import click


@click.group()
@click.version_option()
def cli():
    "CLI suite"
    pass

