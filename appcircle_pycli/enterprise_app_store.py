import click
import json
import logging
from .api import (
    get_enterprise_profiles,
    get_enterprise_app_versions,
    publish_enterprise_app_version,
    unpublish_enterprise_app_version,
    remove_enterprise_app_version,
    notify_enterprise_app_version,
    get_enterprise_download_link,
    upload_enterprise_app_for_profile,
    upload_enterprise_app_without_profile,
)

logger = logging.getLogger(__name__)


@click.group()
def enterprise_app_store():
    """
    Commands for managing the enterprise app store.
    """
    pass


@enterprise_app_store.command(name="list-profiles")
@click.pass_context
def list_profiles(ctx):
    """
    List all enterprise profiles.
    """
    if ctx.obj["debug"]:
        logger.info("Listing all enterprise profiles.")

    try:
        profiles = get_enterprise_profiles()
        click.echo(json.dumps(profiles, indent=2))
    except Exception as e:
        if ctx.obj["debug"]:
            logger.error(f"An error occurred: {e}", exc_info=True)
        else:
            click.echo(f"Error: {e}", err=True)


@enterprise_app_store.command(name="list-versions")
@click.option(
    "--entProfileId", "ent_profile_id", help="Enterprise Profile ID (UUID format)"
)
@click.option(
    "--entProfile",
    "ent_profile",
    help="Enterprise Profile Name instead of 'entProfileId'",
)
@click.option(
    "--publishType",
    "publish_type",
    default="0",
    type=click.Choice(["0", "1", "2"]),
    help="Publish type: 0=All, 1=Beta, 2=Live",
)
@click.pass_context
def list_versions(ctx, ent_profile_id, ent_profile, publish_type):
    """
    List app versions for an enterprise profile.
    """
    if ctx.obj["debug"]:
        logger.info("Listing app versions with the following parameters:")
        logger.info(f"Enterprise Profile ID: {ent_profile_id}")
        logger.info(f"Enterprise Profile Name: {ent_profile}")
        logger.info(f"Publish Type: {publish_type}")

    if not ent_profile_id and not ent_profile:
        raise click.UsageError("Either --entProfileId or --entProfile is required.")

    try:
        versions = get_enterprise_app_versions(
            ent_profile_id or ent_profile, publish_type
        )
        click.echo(json.dumps(versions, indent=2))
    except Exception as e:
        if ctx.obj["debug"]:
            logger.error(f"An error occurred: {e}", exc_info=True)
        else:
            click.echo(f"Error: {e}", err=True)


@enterprise_app_store.command(name="publish")
@click.option(
    "--entProfileId", "ent_profile_id", help="Enterprise Profile ID (UUID format)"
)
@click.option(
    "--entProfile",
    "ent_profile",
    help="Enterprise Profile Name instead of 'entProfileId'",
)
@click.option(
    "--entVersionId",
    "ent_version_id",
    required=True,
    help="Enterprise Version ID (UUID format)",
)
@click.option("--summary", required=True, help="Version summary")
@click.option("--releaseNotes", "release_notes", required=True, help="Release notes")
@click.option(
    "--publishType",
    "publish_type",
    required=True,
    type=click.Choice(["1", "2"]),
    help="Publish type: 1=Beta, 2=Live",
)
@click.pass_context
def publish_version(
    ctx,
    ent_profile_id,
    ent_profile,
    ent_version_id,
    summary,
    release_notes,
    publish_type,
):
    """
    Publish an enterprise app version.
    """
    if ctx.obj["debug"]:
        logger.info(
            "Publishing an enterprise app version with the following parameters:"
        )
        logger.info(f"Enterprise Profile ID: {ent_profile_id}")
        logger.info(f"Enterprise Profile Name: {ent_profile}")
        logger.info(f"Enterprise Version ID: {ent_version_id}")
        logger.info(f"Summary: {summary}")
        logger.info(f"Release Notes: {release_notes}")
        logger.info(f"Publish Type: {publish_type}")

    if not ent_profile_id and not ent_profile:
        raise click.UsageError("Either --entProfileId or --entProfile is required.")

    try:
        response = publish_enterprise_app_version(
            ent_profile_id or ent_profile,
            ent_version_id,
            summary,
            release_notes,
            publish_type,
        )
        click.echo(json.dumps(response, indent=2))
    except Exception as e:
        if ctx.obj["debug"]:
            logger.error(f"An error occurred: {e}", exc_info=True)
        else:
            click.echo(f"Error: {e}", err=True)


@enterprise_app_store.command(name="unpublish")
@click.option(
    "--entProfileId", "ent_profile_id", help="Enterprise Profile ID (UUID format)"
)
@click.option(
    "--entProfile",
    "ent_profile",
    help="Enterprise Profile Name instead of 'entProfileId'",
)
@click.option(
    "--entVersionId",
    "ent_version_id",
    required=True,
    help="Enterprise Version ID (UUID format)",
)
@click.pass_context
def unpublish_version(ctx, ent_profile_id, ent_profile, ent_version_id):
    """
    Unpublish an enterprise app version.
    """
    if ctx.obj["debug"]:
        logger.info(
            "Unpublishing an enterprise app version with the following parameters:"
        )
        logger.info(f"Enterprise Profile ID: {ent_profile_id}")
        logger.info(f"Enterprise Profile Name: {ent_profile}")
        logger.info(f"Enterprise Version ID: {ent_version_id}")

    if not ent_profile_id and not ent_profile:
        raise click.UsageError("Either --entProfileId or --entProfile is required.")

    try:
        response = unpublish_enterprise_app_version(
            ent_profile_id or ent_profile, ent_version_id
        )
        click.echo(json.dumps(response, indent=2))
    except Exception as e:
        if ctx.obj["debug"]:
            logger.error(f"An error occurred: {e}", exc_info=True)
        else:
            click.echo(f"Error: {e}", err=True)


@enterprise_app_store.command(name="remove")
@click.option(
    "--entProfileId", "ent_profile_id", help="Enterprise Profile ID (UUID format)"
)
@click.option(
    "--entProfile",
    "ent_profile",
    help="Enterprise Profile Name instead of 'entProfileId'",
)
@click.option(
    "--entVersionId",
    "ent_version_id",
    required=True,
    help="Enterprise Version ID (UUID format)",
)
@click.pass_context
def remove_version(ctx, ent_profile_id, ent_profile, ent_version_id):
    """
    Remove an enterprise app version.
    """
    if ctx.obj["debug"]:
        logger.info("Removing an enterprise app version with the following parameters:")
        logger.info(f"Enterprise Profile ID: {ent_profile_id}")
        logger.info(f"Enterprise Profile Name: {ent_profile}")
        logger.info(f"Enterprise Version ID: {ent_version_id}")

    if not ent_profile_id and not ent_profile:
        raise click.UsageError("Either --entProfileId or --entProfile is required.")

    try:
        response = remove_enterprise_app_version(
            ent_profile_id or ent_profile, ent_version_id
        )
        click.echo(json.dumps(response, indent=2))
    except Exception as e:
        if ctx.obj["debug"]:
            logger.error(f"An error occurred: {e}", exc_info=True)
        else:
            click.echo(f"Error: {e}", err=True)


@enterprise_app_store.command(name="notify")
@click.option(
    "--entProfileId", "ent_profile_id", help="Enterprise Profile ID (UUID format)"
)
@click.option(
    "--entProfile",
    "ent_profile",
    help="Enterprise Profile Name instead of 'entProfileId'",
)
@click.option(
    "--entVersionId",
    "ent_version_id",
    required=True,
    help="Enterprise Version ID (UUID format)",
)
@click.option("--subject", required=True, help="Notification subject")
@click.option("--message", required=True, help="Notification message")
@click.pass_context
def notify_version(ctx, ent_profile_id, ent_profile, ent_version_id, subject, message):
    """
    Notify users about an enterprise app version.
    """
    if ctx.obj["debug"]:
        logger.info(
            "Notifying users about an enterprise app version with the following parameters:"
        )
        logger.info(f"Enterprise Profile ID: {ent_profile_id}")
        logger.info(f"Enterprise Profile Name: {ent_profile}")
        logger.info(f"Enterprise Version ID: {ent_version_id}")
        logger.info(f"Subject: {subject}")
        logger.info(f"Message: {message}")

    if not ent_profile_id and not ent_profile:
        raise click.UsageError("Either --entProfileId or --entProfile is required.")

    try:
        response = notify_enterprise_app_version(
            ent_profile_id or ent_profile, ent_version_id, subject, message
        )
        click.echo(json.dumps(response, indent=2))
    except Exception as e:
        if ctx.obj["debug"]:
            logger.error(f"An error occurred: {e}", exc_info=True)
        else:
            click.echo(f"Error: {e}", err=True)


@enterprise_app_store.command(name="download-link")
@click.option(
    "--entProfileId", "ent_profile_id", help="Enterprise Profile ID (UUID format)"
)
@click.option(
    "--entProfile",
    "ent_profile",
    help="Enterprise Profile Name instead of 'entProfileId'",
)
@click.option(
    "--entVersionId",
    "ent_version_id",
    required=True,
    help="Enterprise Version ID (UUID format)",
)
@click.pass_context
def download_link(ctx, ent_profile_id, ent_profile, ent_version_id):
    """
    Get the download link for an enterprise app version.
    """
    if ctx.obj["debug"]:
        logger.info(
            "Getting the download link for an enterprise app version with the following parameters:"
        )
        logger.info(f"Enterprise Profile ID: {ent_profile_id}")
        logger.info(f"Enterprise Profile Name: {ent_profile}")
        logger.info(f"Enterprise Version ID: {ent_version_id}")

    if not ent_profile_id and not ent_profile:
        raise click.UsageError("Either --entProfileId or --entProfile is required.")

    try:
        link = get_enterprise_download_link(
            ent_profile_id or ent_profile, ent_version_id
        )
        click.echo(json.dumps(link, indent=2))
    except Exception as e:
        if ctx.obj["debug"]:
            logger.error(f"An error occurred: {e}", exc_info=True)
        else:
            click.echo(f"Error: {e}", err=True)


@click.group()
def version():
    """
    Commands for managing enterprise app versions.
    """
    pass


enterprise_app_store.add_command(version)


@version.command(name="upload-for-profile")
@click.option(
    "--entProfileId", "ent_profile_id", required=True, help="Enterprise Profile ID"
)
@click.option("--app", required=True, help="App file path to upload")
@click.option("--name", required=True, help="App version name")
@click.option("--summary", required=True, help="App version summary")
@click.pass_context
def upload_for_profile(ctx, ent_profile_id, app, name, summary):
    """
    Upload App Version for Enterprise Profile
    """
    if ctx.obj["debug"]:
        logger.info(
            "Uploading an app version for an enterprise profile with the following parameters:"
        )
        logger.info(f"Enterprise Profile ID: {ent_profile_id}")
        logger.info(f"App Path: {app}")
        logger.info(f"Name: {name}")
        logger.info(f"Summary: {summary}")

    try:
        response = upload_enterprise_app_for_profile(ent_profile_id, app, name, summary)
        click.echo(json.dumps(response, indent=2))
    except Exception as e:
        if ctx.obj["debug"]:
            logger.error(f"An error occurred: {e}", exc_info=True)
        else:
            click.echo(f"Error: {e}", err=True)


@version.command(name="upload-without-profile")
@click.option("--app", required=True, help="App file path to upload")
@click.option("--name", required=True, help="App version name")
@click.option("--summary", required=True, help="App version summary")
@click.pass_context
def upload_without_profile(ctx, app, name, summary):
    """
    Upload App Version without Enterprise Profile
    """
    if ctx.obj["debug"]:
        logger.info(
            "Uploading an app version without an enterprise profile with the following parameters:"
        )
        logger.info(f"App Path: {app}")
        logger.info(f"Name: {name}")
        logger.info(f"Summary: {summary}")

    try:
        response = upload_enterprise_app_without_profile(app, name, summary)
        click.echo(json.dumps(response, indent=2))
    except Exception as e:
        if ctx.obj["debug"]:
            logger.error(f"An error occurred: {e}", exc_info=True)
        else:
            click.echo(f"Error: {e}", err=True)
