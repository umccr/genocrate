import click


@click.group(name="genocrate")
@click.version_option()
def cli():
    "CLI suite"
    pass

