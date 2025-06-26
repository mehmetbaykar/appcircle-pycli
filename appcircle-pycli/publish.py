import click
import json
import logging
from .utils import setup_debug_mode
from .api import (
    get_publish_profiles,
    create_publish_profile,
    delete_publish_profile,
    rename_publish_profile,
    get_publish_profile_settings,
    update_publish_profile_settings,
    get_publish_profile_versions,
    delete_publish_profile_version,
    download_publish_profile_version,
    mark_as_rc,
    unmark_as_rc,
    update_release_note,
    get_active_publishes,
    start_existing_publish_flow,
    get_publish_variable_groups,
    get_publish_variable_list_by_group_id,
    upload_publish_environment_variables_from_file,
    get_app_version_detail,
    upload_app_version,
    create_publish_variable_group,
    delete_publish_variable_group,
    download_publish_variables,
)

logger = logging.getLogger(__name__)


@click.group()
def publish():
    """Manage Publish Actions"""
    pass


@click.group()
def profile():
    """Manage Publish Profiles"""
    pass


@click.group(name="settings")
def profile_settings():
    """Manage Profile Settings"""
    pass


@click.group(name="version")
def profile_version():
    """Manage Profile Versions"""
    pass


@click.group()
def variable():
    """Environment Variable Actions"""
    pass


@click.group()
def group():
    """Variable Group Actions"""
    pass


publish.add_command(profile)
profile.add_command(profile_settings)
profile.add_command(profile_version)
publish.add_command(variable)
variable.add_command(group)


@publish.command(name="active-list")
@click.pass_context
def active_list(ctx):
    """Get a List of Active Publish in the Queue"""
    if ctx.obj["debug"]:
        logger.info("Fetching active publishes.")

    try:
        publishes = get_active_publishes()
        click.echo(json.dumps(publishes, indent=2))
    except Exception as e:
        if ctx.obj["debug"]:
            logger.error(f"An error occurred: {e}", exc_info=True)
        else:
            click.echo(f"Error: {e}", err=True)


@publish.command(name="view")
@click.option(
    "--platform",
    required=True,
    type=click.Choice(["iOS", "Android"]),
    help="Platform (iOS/Android)",
)
@click.option(
    "--publishProfileId", "publish_profile_id", help="Publish Profile ID (UUID format)"
)
@click.option(
    "--publishProfile",
    "publish_profile",
    help="Publish Profile Name instead of 'publishProfileId'",
)
@click.option(
    "--appVersionId",
    "app_version_id",
    required=True,
    help="App Version ID (UUID format)",
)
@click.pass_context
def view(ctx, platform, publish_profile_id, publish_profile, app_version_id):
    """View Details of a Publishing Process"""
    if ctx.obj["debug"]:
        logger.info(
            "Viewing details of a publishing process with the following parameters:"
        )
        logger.info(f"Platform: {platform}")
        logger.info(f"Publish Profile ID: {publish_profile_id}")
        logger.info(f"Publish Profile Name: {publish_profile}")
        logger.info(f"App Version ID: {app_version_id}")

    if not publish_profile_id and not publish_profile:
        raise click.UsageError(
            "Either --publishProfileId or --publishProfile is required."
        )

    try:
        response = get_app_version_detail(
            publish_profile_id or publish_profile, platform, app_version_id
        )
        click.echo(json.dumps(response, indent=2))
    except Exception as e:
        if ctx.obj["debug"]:
            logger.error(f"An error occurred: {e}", exc_info=True)
        else:
            click.echo(f"Error: {e}", err=True)


@publish.command()
@click.option(
    "--platform",
    required=True,
    type=click.Choice(["iOS", "Android"]),
    help="Platform (iOS/Android)",
)
@click.option(
    "--publishProfileId", "publish_profile_id", help="Publish Profile ID (UUID format)"
)
@click.option(
    "--publishProfile",
    "publish_profile",
    help="Publish Profile Name instead of 'publishProfileId'",
)
@click.option("--appVersionId", "app_version_id", help="App Version ID (UUID format)")
@click.option(
    "--appVersion", "app_version", help="App Version Name instead of 'appVersionId'"
)
@click.option("--debug", is_flag=True, help="Enable debug mode with verbose output")
@click.pass_context
def start(
    ctx, platform, publish_profile_id, publish_profile, app_version_id, app_version, debug
):
    """Start a New App Publishing Process"""
    debug_enabled = setup_debug_mode(ctx, debug)
    
    if debug_enabled:
        logger.info(
            "Starting a new app publishing process with the following parameters:"
        )
        logger.info(f"Platform: {platform}")
        logger.info(f"Publish Profile ID: {publish_profile_id}")
        logger.info(f"Publish Profile Name: {publish_profile}")
        logger.info(f"App Version ID: {app_version_id}")
        logger.info(f"App Version Name: {app_version}")

    if not publish_profile_id and not publish_profile:
        raise click.UsageError(
            "Either --publishProfileId or --publishProfile is required."
        )
    if not app_version_id and not app_version:
        raise click.UsageError("Either --appVersionId or --appVersion is required.")

    try:
        response = start_existing_publish_flow(
            publish_profile_id or publish_profile,
            platform,
            app_version_id or app_version,
        )
        click.echo(json.dumps(response, indent=2))
    except Exception as e:
        if debug_enabled:
            logger.error(f"An error occurred: {e}", exc_info=True)
        else:
            click.echo(f"Error: {e}", err=True)


@profile.command(name="create")
@click.option(
    "--platform",
    required=True,
    type=click.Choice(["iOS", "Android"]),
    help="Platform (iOS/Android)",
)
@click.option("--name", required=True, help="Publish Profile Name")
@click.pass_context
def profile_create(ctx, platform, name):
    """Create a New Publish Profile"""
    if ctx.obj["debug"]:
        logger.info("Creating a new publish profile with the following parameters:")
        logger.info(f"Platform: {platform}")
        logger.info(f"Name: {name}")

    try:
        response = create_publish_profile(platform, name)
        click.echo(json.dumps(response, indent=2))
    except Exception as e:
        if ctx.obj["debug"]:
            logger.error(f"An error occurred: {e}", exc_info=True)
        else:
            click.echo(f"Error: {e}", err=True)


@profile.command(name="delete")
@click.option(
    "--platform",
    required=True,
    type=click.Choice(["iOS", "Android"]),
    help="Platform (iOS/Android)",
)
@click.option("--profileId", "profile_id", required=True, help="Publish Profile ID")
@click.pass_context
def profile_delete(ctx, platform, profile_id):
    """Delete a Publish Profile"""
    if ctx.obj["debug"]:
        logger.info("Deleting a publish profile with the following parameters:")
        logger.info(f"Platform: {platform}")
        logger.info(f"Profile ID: {profile_id}")

    try:
        response = delete_publish_profile(platform, profile_id)
        click.echo(json.dumps(response, indent=2))
    except Exception as e:
        if ctx.obj["debug"]:
            logger.error(f"An error occurred: {e}", exc_info=True)
        else:
            click.echo(f"Error: {e}", err=True)


@profile.command(name="list")
@click.option(
    "--platform",
    required=True,
    type=click.Choice(["iOS", "Android"]),
    help="Platform (iOS/Android)",
)
@click.pass_context
def profile_list(ctx, platform):
    """Get List of Publish Profiles"""
    if ctx.obj["debug"]:
        logger.info(f"Listing publish profiles for platform: {platform}")

    try:
        profiles = get_publish_profiles(platform)
        click.echo(json.dumps(profiles, indent=2))
    except Exception as e:
        if ctx.obj["debug"]:
            logger.error(f"An error occurred: {e}", exc_info=True)
        else:
            click.echo(f"Error: {e}", err=True)


@profile.command(name="rename")
@click.option(
    "--platform",
    required=True,
    type=click.Choice(["iOS", "Android"]),
    help="Platform (iOS/Android)",
)
@click.option("--profileId", "profile_id", required=True, help="Publish Profile ID")
@click.option("--newName", "new_name", required=True, help="New profile name")
@click.pass_context
def profile_rename(ctx, platform, profile_id, new_name):
    """Rename a Publish Profile"""
    if ctx.obj["debug"]:
        logger.info("Renaming a publish profile with the following parameters:")
        logger.info(f"Platform: {platform}")
        logger.info(f"Profile ID: {profile_id}")
        logger.info(f"New Name: {new_name}")

    try:
        response = rename_publish_profile(platform, profile_id, new_name)
        click.echo(json.dumps(response, indent=2))
    except Exception as e:
        if ctx.obj["debug"]:
            logger.error(f"An error occurred: {e}", exc_info=True)
        else:
            click.echo(f"Error: {e}", err=True)


@profile_settings.command(name="autopublish")
@click.option(
    "--platform",
    required=True,
    type=click.Choice(["iOS", "Android"]),
    help="Platform (iOS/Android)",
)
@click.option("--profileId", "profile_id", required=True, help="Publish Profile ID")
@click.option("--enable/--disable", default=None, help="Enable or disable auto-publish")
@click.pass_context
def profile_settings_autopublish(ctx, platform, profile_id, enable):
    """Configure Auto-publish Settings"""
    if ctx.obj["debug"]:
        logger.info("Configuring auto-publish settings with the following parameters:")
        logger.info(f"Platform: {platform}")
        logger.info(f"Profile ID: {profile_id}")
        logger.info(f"Enable: {enable}")

    try:
        settings = get_publish_profile_settings(platform, profile_id)
        if enable is not None:
            settings["autoPublish"] = enable
            response = update_publish_profile_settings(platform, profile_id, settings)
            click.echo(json.dumps(response, indent=2))
        else:
            click.echo(json.dumps(settings, indent=2))
    except Exception as e:
        if ctx.obj["debug"]:
            logger.error(f"An error occurred: {e}", exc_info=True)
        else:
            click.echo(f"Error: {e}", err=True)


@profile_version.command(name="delete")
@click.option(
    "--platform",
    required=True,
    type=click.Choice(["iOS", "Android"]),
    help="Platform (iOS/Android)",
)
@click.option("--profileId", "profile_id", required=True, help="Publish Profile ID")
@click.option("--versionId", "version_id", required=True, help="App Version ID")
@click.pass_context
def profile_version_delete(ctx, platform, profile_id, version_id):
    """Delete an App Version"""
    if ctx.obj["debug"]:
        logger.info("Deleting an app version with the following parameters:")
        logger.info(f"Platform: {platform}")
        logger.info(f"Profile ID: {profile_id}")
        logger.info(f"Version ID: {version_id}")

    try:
        response = delete_publish_profile_version(platform, profile_id, version_id)
        click.echo(json.dumps(response, indent=2))
    except Exception as e:
        if ctx.obj["debug"]:
            logger.error(f"An error occurred: {e}", exc_info=True)
        else:
            click.echo(f"Error: {e}", err=True)


@profile_version.command(name="download")
@click.option(
    "--platform",
    required=True,
    type=click.Choice(["iOS", "Android"]),
    help="Platform (iOS/Android)",
)
@click.option("--profileId", "profile_id", required=True, help="Publish Profile ID")
@click.option("--versionId", "version_id", required=True, help="App Version ID")
@click.option("--path", required=False, help="Download path for the app version")
@click.pass_context
def profile_version_download(ctx, platform, profile_id, version_id, path):
    """Download an App Version"""
    if ctx.obj["debug"]:
        logger.info("Downloading an app version with the following parameters:")
        logger.info(f"Platform: {platform}")
        logger.info(f"Profile ID: {profile_id}")
        logger.info(f"Version ID: {version_id}")
        logger.info(f"Path: {path}")

    try:
        download_publish_profile_version(platform, profile_id, version_id, path)
    except Exception as e:
        if ctx.obj["debug"]:
            logger.error(f"An error occurred: {e}", exc_info=True)
        else:
            click.echo(f"Error: {e}", err=True)


@profile_version.command(name="list")
@click.option(
    "--platform",
    required=True,
    type=click.Choice(["iOS", "Android"]),
    help="Platform (iOS/Android)",
)
@click.option("--profileId", "profile_id", required=True, help="Publish Profile ID")
@click.pass_context
def profile_version_list(ctx, platform, profile_id):
    """List App Versions of a Publish Profile"""
    if ctx.obj["debug"]:
        logger.info(
            "Listing app versions of a publish profile with the following parameters:"
        )
        logger.info(f"Platform: {platform}")
        logger.info(f"Profile ID: {profile_id}")

    try:
        versions = get_publish_profile_versions(platform, profile_id)
        click.echo(json.dumps(versions, indent=2))
    except Exception as e:
        if ctx.obj["debug"]:
            logger.error(f"An error occurred: {e}", exc_info=True)
        else:
            click.echo(f"Error: {e}", err=True)


@profile_version.command(name="view")
@click.option(
    "--platform",
    required=True,
    type=click.Choice(["iOS", "Android"]),
    help="Platform (iOS/Android)",
)
@click.option("--profileId", "profile_id", required=True, help="Publish Profile ID")
@click.option("--versionId", "version_id", required=True, help="App Version ID")
@click.pass_context
def profile_version_view(ctx, platform, profile_id, version_id):
    """View Details of an App Version"""
    if ctx.obj["debug"]:
        logger.info("Getting app version details with the following parameters:")
        logger.info(f"Platform: {platform}")
        logger.info(f"Profile ID: {profile_id}")
        logger.info(f"Version ID: {version_id}")

    try:
        version_detail = get_app_version_detail(profile_id, platform, version_id)
        click.echo(json.dumps(version_detail, indent=2))
    except Exception as e:
        if ctx.obj["debug"]:
            logger.error(f"An error occurred: {e}", exc_info=True)
        else:
            click.echo(f"Error: {e}", err=True)


@profile_version.command(name="mark-as-rc")
@click.option(
    "--platform",
    required=True,
    type=click.Choice(["iOS", "Android"]),
    help="Platform (iOS/Android)",
)
@click.option("--profileId", "profile_id", required=True, help="Publish Profile ID")
@click.option("--versionId", "version_id", required=True, help="App Version ID")
@click.pass_context
def profile_version_mark_as_rc(ctx, platform, profile_id, version_id):
    """Mark App Version as Release Candidate"""
    if ctx.obj["debug"]:
        logger.info(
            "Marking an app version as a release candidate with the following parameters:"
        )
        logger.info(f"Platform: {platform}")
        logger.info(f"Profile ID: {profile_id}")
        logger.info(f"Version ID: {version_id}")

    try:
        response = mark_as_rc(platform, profile_id, version_id)
        click.echo(json.dumps(response, indent=2))
    except Exception as e:
        if ctx.obj["debug"]:
            logger.error(f"An error occurred: {e}", exc_info=True)
        else:
            click.echo(f"Error: {e}", err=True)


@profile_version.command(name="unmark-as-rc")
@click.option(
    "--platform",
    required=True,
    type=click.Choice(["iOS", "Android"]),
    help="Platform (iOS/Android)",
)
@click.option("--profileId", "profile_id", required=True, help="Publish Profile ID")
@click.option("--versionId", "version_id", required=True, help="App Version ID")
@click.pass_context
def profile_version_unmark_as_rc(ctx, platform, profile_id, version_id):
    """Unmark App Version as Release Candidate"""
    if ctx.obj["debug"]:
        logger.info(
            "Unmarking an app version as a release candidate with the following parameters:"
        )
        logger.info(f"Platform: {platform}")
        logger.info(f"Profile ID: {profile_id}")
        logger.info(f"Version ID: {version_id}")

    try:
        response = unmark_as_rc(platform, profile_id, version_id)
        click.echo(json.dumps(response, indent=2))
    except Exception as e:
        if ctx.obj["debug"]:
            logger.error(f"An error occurred: {e}", exc_info=True)
        else:
            click.echo(f"Error: {e}", err=True)


@profile_version.command(name="update-release-note")
@click.option(
    "--platform",
    required=True,
    type=click.Choice(["iOS", "Android"]),
    help="Platform (iOS/Android)",
)
@click.option("--profileId", "profile_id", required=True, help="Publish Profile ID")
@click.option("--versionId", "version_id", required=True, help="App Version ID")
@click.option("--note", required=True, help="Release note text")
@click.pass_context
def profile_version_update_release_note(ctx, platform, profile_id, version_id, note):
    """Update Release Notes of an App Version"""
    if ctx.obj["debug"]:
        logger.info(
            "Updating the release notes of an app version with the following parameters:"
        )
        logger.info(f"Platform: {platform}")
        logger.info(f"Profile ID: {profile_id}")
        logger.info(f"Version ID: {version_id}")
        logger.info(f"Note: {note}")

    try:
        response = update_release_note(platform, profile_id, version_id, note)
        click.echo(json.dumps(response, indent=2))
    except Exception as e:
        if ctx.obj["debug"]:
            logger.error(f"An error occurred: {e}", exc_info=True)
        else:
            click.echo(f"Error: {e}", err=True)


@profile_version.command(name="upload")
@click.option("--app", required=True, help="App file path to upload")
@click.option("--profileId", "profile_id", required=True, help="Publish Profile ID")
@click.option(
    "--platform",
    required=True,
    type=click.Choice(["iOS", "Android"]),
    help="Platform (iOS/Android)",
)
@click.pass_context
def profile_version_upload(ctx, app, profile_id, platform):
    """Upload a New App Version to Publish Profile"""
    if ctx.obj["debug"]:
        logger.info(
            "Uploading a new app version to a publish profile with the following parameters:"
        )
        logger.info(f"App Path: {app}")
        logger.info(f"Profile ID: {profile_id}")
        logger.info(f"Platform: {platform}")

    try:
        response = upload_app_version(app, profile_id, platform)
        click.echo(json.dumps(response, indent=2))
    except Exception as e:
        if ctx.obj["debug"]:
            logger.error(f"An error occurred: {e}", exc_info=True)
        else:
            click.echo(f"Error: {e}", err=True)


@group.command(name="list")
@click.pass_context
def variable_group_list(ctx):
    """List Publishing Variable Groups"""
    if ctx.obj["debug"]:
        logger.info("Listing publishing variable groups.")

    try:
        groups = get_publish_variable_groups()
        click.echo(json.dumps(groups, indent=2))
    except Exception as e:
        if ctx.obj["debug"]:
            logger.error(f"An error occurred: {e}", exc_info=True)
        else:
            click.echo(f"Error: {e}", err=True)


@group.command(name="create")
@click.option("--name", required=True, help="Variable Group Name")
@click.pass_context
def variable_group_create(ctx, name):
    """Create a New Publishing Variable Group"""
    if ctx.obj["debug"]:
        logger.info(f"Creating a new publishing variable group with name: {name}")

    try:
        group = create_publish_variable_group(name)
        click.echo(json.dumps(group, indent=2))
    except Exception as e:
        if ctx.obj["debug"]:
            logger.error(f"An error occurred: {e}", exc_info=True)
        else:
            click.echo(f"Error: {e}", err=True)


@group.command(name="delete")
@click.option("--groupId", "group_id", required=True, help="Variable Group ID")
@click.pass_context
def variable_group_delete(ctx, group_id):
    """Delete a Publishing Variable Group"""
    if ctx.obj["debug"]:
        logger.info(f"Deleting a publishing variable group with ID: {group_id}")

    try:
        result = delete_publish_variable_group(group_id)
        click.echo(json.dumps(result, indent=2))
    except Exception as e:
        if ctx.obj["debug"]:
            logger.error(f"An error occurred: {e}", exc_info=True)
        else:
            click.echo(f"Error: {e}", err=True)


@group.command(name="view")
@click.option("--groupId", "group_id", required=True, help="Variable Group ID")
@click.pass_context
def variable_group_view(ctx, group_id):
    """View Details of a Publishing Variable Group"""
    if ctx.obj["debug"]:
        logger.info(
            f"Viewing details of a publishing variable group with ID: {group_id}"
        )

    try:
        variables = get_publish_variable_list_by_group_id(group_id)
        click.echo(json.dumps(variables, indent=2))
    except Exception as e:
        if ctx.obj["debug"]:
            logger.error(f"An error occurred: {e}", exc_info=True)
        else:
            click.echo(f"Error: {e}", err=True)


@group.command(name="upload")
@click.option("--groupId", "group_id", required=True, help="Variable Group ID")
@click.option(
    "--filePath", "file_path", required=True, help="JSON file path containing variables"
)
@click.pass_context
def variable_group_upload(ctx, group_id, file_path):
    """Upload Environment Variables from JSON File"""
    if ctx.obj["debug"]:
        logger.info(
            "Uploading environment variables from a JSON file with the following parameters:"
        )
        logger.info(f"Group ID: {group_id}")
        logger.info(f"File Path: {file_path}")

    try:
        response = upload_publish_environment_variables_from_file(group_id, file_path)
        click.echo(json.dumps(response, indent=2))
    except Exception as e:
        if ctx.obj["debug"]:
            logger.error(f"An error occurred: {e}", exc_info=True)
        else:
            click.echo(f"Error: {e}", err=True)


@group.command(name="download")
@click.option("--groupId", "group_id", required=True, help="Variable Group ID")
@click.option("--path", required=False, help="Download path for the JSON file")
@click.pass_context
def variable_group_download(ctx, group_id, path):
    """Download Publishing Variables as JSON File"""
    if ctx.obj["debug"]:
        logger.info(
            "Downloading publishing variables as a JSON file with the following parameters:"
        )
        logger.info(f"Group ID: {group_id}")
        logger.info(f"Path: {path}")

    try:
        download_publish_variables(group_id, path)
    except Exception as e:
        if ctx.obj["debug"]:
            logger.error(f"An error occurred: {e}", exc_info=True)
        else:
            click.echo(f"Error: {e}", err=True)