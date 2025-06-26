import click
from . import __version__
from .config import config
from .login import login
from .build import build
from .signing_identity import signing_identity
from .publish import publish
from .distribution import distribution
from .testing_distribution import testing_distribution
from .enterprise_app_store import enterprise_app_store
from .organization import organization


@click.group(invoke_without_command=True)
@click.option("--debug", is_flag=True, help="Enable debug mode with verbose output")
@click.option("--version", is_flag=True, help="Show version and exit")
@click.pass_context
def cli(ctx, debug, version):
    """Appcircle CLI"""
    if version:
        click.echo(f"appcircle-pycli {__version__}")
        ctx.exit(0)
    
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())
        ctx.exit(0)
    
    ctx.ensure_object(dict)
    ctx.obj["debug"] = debug
    if debug:
        import logging

        logging.basicConfig(level=logging.DEBUG)
        click.echo("Debug mode enabled", err=True)


cli.add_command(config)
cli.add_command(login)
cli.add_command(build)
cli.add_command(signing_identity)
cli.add_command(publish)
cli.add_command(distribution)
cli.add_command(testing_distribution)
cli.add_command(enterprise_app_store)
cli.add_command(organization)

if __name__ == "__main__":
    cli()
