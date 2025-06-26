import click
import json
import os
import subprocess  # nosec
import sys
import logging
from .config_manager import ConfigManager
from .utils import setup_debug_mode

logger = logging.getLogger(__name__)


@click.group()
def config():
    """View and set Appcircle CLI properties"""
    pass


@config.command(name="list")
@click.option("--debug", is_flag=True, help="Enable debug mode with verbose output")
@click.pass_context
def list_(ctx, debug):
    """List Appcircle CLI properties for All Configurations"""
    debug_enabled = setup_debug_mode(ctx, debug)
    
    if debug_enabled:
        logger.info("Listing all configurations.")

    try:
        config_manager = ConfigManager()
        config = config_manager.get_config()
        click.echo(json.dumps(config, indent=2))
    except Exception as e:
        if debug_enabled:
            logger.error(f"An error occurred: {e}", exc_info=True)
        else:
            click.echo(f"Error: {e}", err=True)


@config.command()
@click.argument("key")
@click.pass_context
def get(ctx, key):
    """Get Print the value of a Appcircle CLI Currently Active Configuration property"""
    if ctx.obj["debug"]:
        logger.info(f"Getting value for key: {key}")

    config_manager = ConfigManager()
    config = config_manager.get_config()
    current_env = config["current"]
    value = config["envs"].get(current_env, {}).get(key)
    click.echo(value)


@config.command()
@click.argument("key")
@click.argument("value")
@click.pass_context
def set(ctx, key, value):
    """Set a Appcircle CLI Currently Active Configuration property"""
    if ctx.obj["debug"]:
        logger.info(f"Setting value for key: {key} to: {value}")

    config_manager = ConfigManager()
    config = config_manager.get_config()
    current_env = config["current"]
    if current_env not in config["envs"]:
        config["envs"][current_env] = {}
    config["envs"][current_env][key] = value
    config_manager.set_config(config)
    click.echo(f"Property {key} set to {value}")


@config.command()
@click.argument("env")
@click.pass_context
def current(ctx, env):
    """Set a Appcircle CLI Currently Active Configuration Environment"""
    if ctx.obj["debug"]:
        logger.info(f"Setting current environment to: {env}")

    config_manager = ConfigManager()
    config = config_manager.get_config()
    if env not in config["envs"]:
        click.echo(
            f"Environment {env} does not exist. Use 'appcircle config add {env}' to create it."
        )
        return
    config["current"] = env
    config_manager.set_config(config)
    click.echo(f"Current environment set to {env}")


@config.command()
@click.argument("env")
@click.pass_context
def add(ctx, env):
    """Add a New Appcircle CLI Configuration Environment"""
    if ctx.obj["debug"]:
        logger.info(f"Adding new environment: {env}")

    config_manager = ConfigManager()
    config = config_manager.get_config()
    if env in config["envs"]:
        click.echo(f"Environment {env} already exists.")
        return
    config["envs"][env] = {
        "API_HOSTNAME": "https://api.appcircle.io",
        "AUTH_HOSTNAME": "https://auth.appcircle.io",
        "AC_ACCESS_TOKEN": None,
    }
    config_manager.set_config(config)
    click.echo(f"Environment {env} added.")


@config.command()
@click.pass_context
def reset(ctx):
    """Reset a Appcircle CLI Configuration to default"""
    if ctx.obj["debug"]:
        logger.info("Resetting current environment to default.")

    config_manager = ConfigManager()
    config = config_manager.get_config()
    current_env = config["current"]
    config["envs"][current_env] = {
        "API_HOSTNAME": "https://api.appcircle.io",
        "AUTH_HOSTNAME": "https://auth.appcircle.io",
        "AC_ACCESS_TOKEN": None,
    }
    config_manager.set_config(config)
    click.echo(f"Environment {current_env} has been reset to default.")


@config.command()
@click.pass_context
def trust(ctx):
    """Trust the SSL Certificate of the self-hosted Appcircle Server"""
    if ctx.obj["debug"]:
        logger.info("Trusting SSL certificate.")

    if sys.platform not in ["darwin", "linux"]:
        click.echo(
            "Error: This command is supported on macOS and Linux only.", err=True
        )
        return

    script_path = os.path.join(
        os.path.dirname(__file__), "..", "..", "scripts", "install_cert.sh"
    )
    config_manager = ConfigManager()
    config = config_manager.get_config()
    current_env = config["current"]
    api_hostname = config["envs"].get(current_env, {}).get("API_HOSTNAME")

    if not api_hostname:
        click.echo("API_HOSTNAME is not set in the current environment.", err=True)
        return

    process = subprocess.Popen(  # nosec
        ["bash", script_path, api_hostname],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    stdout, stderr = process.communicate()

    if stdout:
        click.echo(stdout.decode())
    if stderr:
        click.echo(stderr.decode(), err=True)