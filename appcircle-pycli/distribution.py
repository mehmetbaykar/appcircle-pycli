import click
import json
import logging
from .api import (
    get_distribution_profiles,
    get_distribution_profile_by_id,
    update_distribution_profile_settings,
    create_distribution_profile,
    get_testing_groups,
    get_testing_group_by_id,
    create_testing_group,
    delete_testing_group,
    add_tester_to_testing_group,
    remove_tester_from_testing_group,
    get_testing_distribution_upload_information,
    commit_testing_distribution_file_upload,
    update_testing_distribution_release_notes,
)

logger = logging.getLogger(__name__)


@click.group()
def distribution():
    """
    Commands for managing distribution profiles.
    """
    pass


@distribution.command(name="list")
@click.pass_context
def list_profiles(ctx):
    """
    List all distribution profiles.
    """
    if ctx.obj["debug"]:
        logger.info("Listing all distribution profiles.")

    try:
        profiles = get_distribution_profiles()
        click.echo(json.dumps(profiles, indent=2))
    except Exception as e:
        if ctx.obj["debug"]:
            logger.error(f"An error occurred: {e}", exc_info=True)
        else:
            click.echo(f"Error: {e}", err=True)


@distribution.command(name="view")
@click.argument("dist_profile_id")
@click.pass_context
def view_profile(ctx, dist_profile_id):
    """
    View a specific distribution profile.
    """
    if ctx.obj["debug"]:
        logger.info(f"Viewing distribution profile with ID: {dist_profile_id}")

    try:
        profile = get_distribution_profile_by_id(dist_profile_id)
        click.echo(json.dumps(profile, indent=2))
    except Exception as e:
        if ctx.obj["debug"]:
            logger.error(f"An error occurred: {e}", exc_info=True)
        else:
            click.echo(f"Error: {e}", err=True)


@distribution.command(name="update-settings")
@click.argument("dist_profile_id")
@click.option("--testing-group-ids", multiple=True)
@click.pass_context
def update_settings(ctx, dist_profile_id, testing_group_ids):
    """
    Update distribution profile settings.
    """
    if ctx.obj["debug"]:
        logger.info(
            f"Updating settings for distribution profile with ID: {dist_profile_id}"
        )
        logger.info(f"Testing group IDs: {testing_group_ids}")

    try:
        response = update_distribution_profile_settings(
            dist_profile_id, testing_group_ids
        )
        click.echo(json.dumps(response, indent=2))
    except Exception as e:
        if ctx.obj["debug"]:
            logger.error(f"An error occurred: {e}", exc_info=True)
        else:
            click.echo(f"Error: {e}", err=True)


@distribution.command(name="create")
@click.argument("name")
@click.pass_context
def create_profile(ctx, name):
    """
    Create a new distribution profile.
    """
    if ctx.obj["debug"]:
        logger.info(f"Creating a new distribution profile with name: {name}")

    try:
        response = create_distribution_profile(name)
        click.echo(json.dumps(response, indent=2))
    except Exception as e:
        if ctx.obj["debug"]:
            logger.error(f"An error occurred: {e}", exc_info=True)
        else:
            click.echo(f"Error: {e}", err=True)


@click.group()
def testing_group():
    """
    Commands for managing testing groups.
    """
    pass


distribution.add_command(testing_group)


@testing_group.command(name="list")
@click.pass_context
def list_testing_groups(ctx):
    """
    List all testing groups.
    """
    if ctx.obj["debug"]:
        logger.info("Listing all testing groups.")

    try:
        groups = get_testing_groups()
        click.echo(json.dumps(groups, indent=2))
    except Exception as e:
        if ctx.obj["debug"]:
            logger.error(f"An error occurred: {e}", exc_info=True)
        else:
            click.echo(f"Error: {e}", err=True)


@testing_group.command(name="view")
@click.argument("testing_group_id")
@click.pass_context
def view_testing_group(ctx, testing_group_id):
    """
    View a specific testing group.
    """
    if ctx.obj["debug"]:
        logger.info(f"Viewing testing group with ID: {testing_group_id}")

    try:
        group = get_testing_group_by_id(testing_group_id)
        click.echo(json.dumps(group, indent=2))
    except Exception as e:
        if ctx.obj["debug"]:
            logger.error(f"An error occurred: {e}", exc_info=True)
        else:
            click.echo(f"Error: {e}", err=True)


@testing_group.command(name="create")
@click.argument("name")
@click.pass_context
def create_group(ctx, name):
    """
    Create a new testing group.
    """
    if ctx.obj["debug"]:
        logger.info(f"Creating a new testing group with name: {name}")

    try:
        response = create_testing_group(name)
        click.echo(json.dumps(response, indent=2))
    except Exception as e:
        if ctx.obj["debug"]:
            logger.error(f"An error occurred: {e}", exc_info=True)
        else:
            click.echo(f"Error: {e}", err=True)


@testing_group.command(name="delete")
@click.argument("testing_group_id")
@click.pass_context
def delete_group(ctx, testing_group_id):
    """
    Delete a testing group.
    """
    if ctx.obj["debug"]:
        logger.info(f"Deleting testing group with ID: {testing_group_id}")

    try:
        response = delete_testing_group(testing_group_id)
        click.echo(json.dumps(response, indent=2))
    except Exception as e:
        if ctx.obj["debug"]:
            logger.error(f"An error occurred: {e}", exc_info=True)
        else:
            click.echo(f"Error: {e}", err=True)


@testing_group.command(name="add-tester")
@click.argument("testing_group_id")
@click.argument("tester_email")
@click.pass_context
def add_tester(ctx, testing_group_id, tester_email):
    """
    Add a tester to a testing group.
    """
    if ctx.obj["debug"]:
        logger.info(
            f"Adding tester {tester_email} to testing group with ID: {testing_group_id}"
        )

    try:
        response = add_tester_to_testing_group(testing_group_id, tester_email)
        click.echo(json.dumps(response, indent=2))
    except Exception as e:
        if ctx.obj["debug"]:
            logger.error(f"An error occurred: {e}", exc_info=True)
        else:
            click.echo(f"Error: {e}", err=True)


@testing_group.command(name="remove-tester")
@click.argument("testing_group_id")
@click.argument("tester_email")
@click.pass_context
def remove_tester(ctx, testing_group_id, tester_email):
    """
    Remove a tester from a testing group.
    """
    if ctx.obj["debug"]:
        logger.info(
            f"Removing tester {tester_email} from testing group with ID: {testing_group_id}"
        )

    try:
        response = remove_tester_from_testing_group(testing_group_id, tester_email)
        click.echo(json.dumps(response, indent=2))
    except Exception as e:
        if ctx.obj["debug"]:
            logger.error(f"An error occurred: {e}", exc_info=True)
        else:
            click.echo(f"Error: {e}", err=True)


@distribution.command(name="upload-info")
@click.argument("dist_profile_id")
@click.option("--file-size", required=True, type=int)
@click.option("--file-name", required=True)
@click.pass_context
def upload_info(ctx, dist_profile_id, file_size, file_name):
    """
    Get upload information for a testing distribution.
    """
    if ctx.obj["debug"]:
        logger.info(
            f"Getting upload information for distribution profile with ID: {dist_profile_id}"
        )
        logger.info(f"File size: {file_size}")
        logger.info(f"File name: {file_name}")

    try:
        info = get_testing_distribution_upload_information(
            dist_profile_id, file_size, file_name
        )
        click.echo(json.dumps(info, indent=2))
    except Exception as e:
        if ctx.obj["debug"]:
            logger.error(f"An error occurred: {e}", exc_info=True)
        else:
            click.echo(f"Error: {e}", err=True)


@distribution.command(name="commit-upload")
@click.argument("dist_profile_id")
@click.option("--file-id", required=True)
@click.option("--file-name", required=True)
@click.pass_context
def commit_upload(ctx, dist_profile_id, file_id, file_name):
    """
    Commit a testing distribution file upload.
    """
    if ctx.obj["debug"]:
        logger.info(
            f"Committing upload for distribution profile with ID: {dist_profile_id}"
        )
        logger.info(f"File ID: {file_id}")
        logger.info(f"File name: {file_name}")

    try:
        response = commit_testing_distribution_file_upload(
            dist_profile_id, file_id, file_name
        )
        click.echo(json.dumps(response, indent=2))
    except Exception as e:
        if ctx.obj["debug"]:
            logger.error(f"An error occurred: {e}", exc_info=True)
        else:
            click.echo(f"Error: {e}", err=True)


@distribution.command(name="update-notes")
@click.argument("dist_profile_id")
@click.argument("version_id")
@click.argument("message")
@click.pass_context
def update_notes(ctx, dist_profile_id, version_id, message):
    """
    Update testing distribution release notes.
    """
    if ctx.obj["debug"]:
        logger.info(
            f"Updating release notes for distribution profile with ID: {dist_profile_id}"
        )
        logger.info(f"Version ID: {version_id}")
        logger.info(f"Message: {message}")

    try:
        response = update_testing_distribution_release_notes(
            dist_profile_id, version_id, message
        )
        click.echo(json.dumps(response, indent=2))
    except Exception as e:
        if ctx.obj["debug"]:
            logger.error(f"An error occurred: {e}", exc_info=True)
        else:
            click.echo(f"Error: {e}", err=True)
