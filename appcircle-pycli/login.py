import click
import requests
import logging
from .config_manager import ConfigManager
from .utils import setup_debug_mode

logger = logging.getLogger(__name__)


@click.command()
@click.option("--pat", "pat", required=True, help="Personal Access Token")
@click.option("--debug", is_flag=True, help="Enable debug mode with verbose output")
@click.pass_context
def login(ctx, pat, debug):
    """Authenticate with Appcircle using your Personal Access Token"""
    debug_enabled = setup_debug_mode(ctx, debug)
    
    if debug_enabled:
        logger.info("Attempting to log in.")

    try:
        config_manager = ConfigManager()
        config = config_manager.get_config()
        current_env = config.get("current", "default")

        if current_env not in config["envs"]:
            config["envs"][current_env] = {}

        auth_hostname = (
            config["envs"][current_env]
            .get("AUTH_HOSTNAME", "https://auth.appcircle.io")
            .rstrip("/")
        )
        auth_endpoint = "/auth/v1/token"

        if debug_enabled:
            logger.info(f"Authenticating with {auth_hostname}{auth_endpoint}")

        response = requests.post(
            f"{auth_hostname}{auth_endpoint}",
            data={"pat": pat},
            headers={
                "accept": "application/json",
                "content-type": "application/x-www-form-urlencoded",
            },
            timeout=30,
        )
        response.raise_for_status()

        token_data = response.json()
        access_token = token_data.get("access_token")

        if not access_token:
            raise Exception("Authentication failed: access_token missing in response")

        config["envs"][current_env]["AC_ACCESS_TOKEN"] = access_token
        config_manager.set_config(config)

        click.echo("Login successful.")
        click.echo(f'export AC_ACCESS_TOKEN="{access_token}"')

    except Exception as e:
        if debug_enabled:
            logger.error(f"An error occurred: {e}", exc_info=True)
        else:
            click.echo(f"Error: {e}", err=True)