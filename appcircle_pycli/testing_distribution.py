import click
import json
import logging
from .api import (
    get_distribution_profiles,
    create_distribution_profile,
    get_testing_distribution_profile_settings,
    update_testing_distribution_auto_send_settings,
    get_testing_groups,
    get_testing_group_by_id,
    create_testing_group,
    delete_testing_group,
    add_tester_to_testing_group,
    remove_tester_from_testing_group,
    upload_testing_distribution,
    add_tester_to_distribution_profile,
    remove_tester_from_distribution_profile,
    add_testing_group_to_distribution_profile,
    remove_testing_group_from_distribution_profile,
    add_workflow_to_distribution_profile,
    remove_workflow_from_distribution_profile,
)

logger = logging.getLogger(__name__)


@click.group(name="testing-distribution")
def testing_distribution():
    """Manage mobile app testing distribution"""
    pass


@click.group()
def profile():
    """Distribution Profile Actions"""
    pass


@click.group(name="settings")
def profile_settings():
    """Configure Distribution Profile Settings"""
    pass


@click.group(name="testing-group")
def testing_group():
    """Testing Group Actions"""
    pass


@click.group()
def tester():
    """Testing Group Tester Actions"""
    pass


testing_distribution.add_command(profile)
profile.add_command(profile_settings)
testing_distribution.add_command(testing_group)
testing_group.add_command(tester)


@testing_distribution.command()
@click.option(
    "--distProfileId", "dist_profile_id", help="Distribution Profile ID (UUID format)"
)
@click.option(
    "--distProfile",
    "dist_profile",
    help="Distribution Profile Name instead of 'distProfileId'",
)
@click.option("--app", required=True, help="App file path to upload")
@click.option("--message", help="Release message for testers")
@click.pass_context
def upload(ctx, dist_profile_id, dist_profile, app, message):
    """Upload Mobile Apps to Distribution Profiles"""
    if ctx.obj["debug"]:
        logger.info(
            "Uploading a mobile app to a distribution profile with the following parameters:"
        )
        logger.info(f"Distribution Profile ID: {dist_profile_id}")
        logger.info(f"Distribution Profile Name: {dist_profile}")
        logger.info(f"App Path: {app}")
        logger.info(f"Message: {message}")

    if not dist_profile_id and not dist_profile:
        raise click.UsageError("Either --distProfileId or --distProfile is required.")

    try:
        result = upload_testing_distribution(
            dist_profile_id or dist_profile, app, message
        )
        click.echo(json.dumps(result, indent=2))
    except Exception as e:
        if ctx.obj["debug"]:
            logger.error(f"An error occurred: {e}", exc_info=True)
        else:
            click.echo(f"Error: {e}", err=True)


@profile.command(name="list")
@click.pass_context
def profile_list(ctx):
    """Get List of Distribution Profiles"""
    if ctx.obj["debug"]:
        logger.info("Listing distribution profiles.")

    try:
        profiles = get_distribution_profiles()
        click.echo(json.dumps(profiles, indent=2))
    except Exception as e:
        if ctx.obj["debug"]:
            logger.error(f"An error occurred: {e}", exc_info=True)
        else:
            click.echo(f"Error: {e}", err=True)


@profile.command(name="create")
@click.option("--name", required=True, help="Distribution Profile Name")
@click.pass_context
def profile_create(ctx, name):
    """Create a New Distribution Profile"""
    if ctx.obj["debug"]:
        logger.info(f"Creating a new distribution profile with name: {name}")

    try:
        result = create_distribution_profile(name)
        click.echo(json.dumps(result, indent=2))
    except Exception as e:
        if ctx.obj["debug"]:
            logger.error(f"An error occurred: {e}", exc_info=True)
        else:
            click.echo(f"Error: {e}", err=True)


@profile_settings.command(name="auto-send")
@click.option(
    "--distProfileId", "dist_profile_id", help="Distribution Profile ID (UUID format)"
)
@click.option(
    "--distProfile",
    "dist_profile",
    help="Distribution Profile Name instead of 'distProfileId'",
)
@click.option(
    "--testingGroupIds", "testing_group_ids", multiple=True, help="Testing Group IDs"
)
@click.option("--enable/--disable", default=None, help="Enable or disable auto-send")
@click.pass_context
def auto_send_settings(ctx, dist_profile_id, dist_profile, testing_group_ids, enable):
    """Configure Automated Distribution to Testing Groups"""
    if ctx.obj["debug"]:
        logger.info(
            "Configuring automated distribution to testing groups with the following parameters:"
        )
        logger.info(f"Distribution Profile ID: {dist_profile_id}")
        logger.info(f"Distribution Profile Name: {dist_profile}")
        logger.info(f"Testing Group IDs: {testing_group_ids}")
        logger.info(f"Enable: {enable}")

    if not dist_profile_id and not dist_profile:
        raise click.UsageError("Either --distProfileId or --distProfile is required.")

    try:
        if enable is not None:
            result = update_testing_distribution_auto_send_settings(
                dist_profile_id or dist_profile, list(testing_group_ids), enable
            )
            click.echo(json.dumps(result, indent=2))
        else:
            settings = get_testing_distribution_profile_settings(
                dist_profile_id or dist_profile
            )
            click.echo(json.dumps(settings, indent=2))
    except Exception as e:
        if ctx.obj["debug"]:
            logger.error(f"An error occurred: {e}", exc_info=True)
        else:
            click.echo(f"Error: {e}", err=True)


@testing_group.command(name="list")
@click.pass_context
def testing_group_list(ctx):
    """Get All Testing Groups"""
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
@click.option(
    "--testingGroupId", "testing_group_id", required=True, help="Testing Group ID"
)
@click.pass_context
def testing_group_view(ctx, testing_group_id):
    """View Details of a Testing Group"""
    if ctx.obj["debug"]:
        logger.info(f"Viewing details of a testing group with ID: {testing_group_id}")

    try:
        group = get_testing_group_by_id(testing_group_id)
        click.echo(json.dumps(group, indent=2))
    except Exception as e:
        if ctx.obj["debug"]:
            logger.error(f"An error occurred: {e}", exc_info=True)
        else:
            click.echo(f"Error: {e}", err=True)


@testing_group.command(name="create")
@click.option("--name", required=True, help="Testing Group Name")
@click.pass_context
def testing_group_create(ctx, name):
    """Create a New Testing Group"""
    if ctx.obj["debug"]:
        logger.info(f"Creating a new testing group with name: {name}")

    try:
        result = create_testing_group(name)
        click.echo(json.dumps(result, indent=2))
    except Exception as e:
        if ctx.obj["debug"]:
            logger.error(f"An error occurred: {e}", exc_info=True)
        else:
            click.echo(f"Error: {e}", err=True)


@testing_group.command(name="remove")
@click.option(
    "--testingGroupId", "testing_group_id", required=True, help="Testing Group ID"
)
@click.pass_context
def testing_group_remove(ctx, testing_group_id):
    """Remove Testing Group"""
    if ctx.obj["debug"]:
        logger.info(f"Removing a testing group with ID: {testing_group_id}")

    try:
        result = delete_testing_group(testing_group_id)
        click.echo(json.dumps(result, indent=2))
    except Exception as e:
        if ctx.obj["debug"]:
            logger.error(f"An error occurred: {e}", exc_info=True)
        else:
            click.echo(f"Error: {e}", err=True)


@tester.command(name="add")
@click.option(
    "--testingGroupId", "testing_group_id", required=True, help="Testing Group ID"
)
@click.option("--email", required=True, help="Tester Email Address")
@click.pass_context
def tester_add(ctx, testing_group_id, email):
    """Add Tester to Testing Group"""
    if ctx.obj["debug"]:
        logger.info("Adding a tester to a testing group with the following parameters:")
        logger.info(f"Testing Group ID: {testing_group_id}")
        logger.info(f"Email: {email}")

    try:
        result = add_tester_to_testing_group(testing_group_id, email)
        click.echo(json.dumps(result, indent=2))
    except Exception as e:
        if ctx.obj["debug"]:
            logger.error(f"An error occurred: {e}", exc_info=True)
        else:
            click.echo(f"Error: {e}", err=True)


@tester.command(name="remove")
@click.option(
    "--testingGroupId", "testing_group_id", required=True, help="Testing Group ID"
)
@click.option("--email", required=True, help="Tester Email Address")
@click.pass_context
def tester_remove(ctx, testing_group_id, email):
    """Remove Tester from Testing Group"""
    if ctx.obj["debug"]:
        logger.info(
            "Removing a tester from a testing group with the following parameters:"
        )
        logger.info(f"Testing Group ID: {testing_group_id}")
        logger.info(f"Email: {email}")

    try:
        result = remove_tester_from_testing_group(testing_group_id, email)
        click.echo(json.dumps(result, indent=2))
    except Exception as e:
        if ctx.obj["debug"]:
            logger.error(f"An error occurred: {e}", exc_info=True)
        else:
            click.echo(f"Error: {e}", err=True)


@profile_settings.command(name="add-tester")
@click.option(
    "--distProfileId", "dist_profile_id", help="Distribution Profile ID (UUID format)"
)
@click.option(
    "--distProfile",
    "dist_profile",
    help="Distribution Profile Name instead of 'distProfileId'",
)
@click.option("--email", required=True, help="Tester Email Address")
@click.pass_context
def profile_add_tester(ctx, dist_profile_id, dist_profile, email):
    """Add Tester to Distribution Profile"""
    if ctx.obj["debug"]:
        logger.info(
            "Adding a tester to a distribution profile with the following parameters:"
        )
        logger.info(f"Distribution Profile ID: {dist_profile_id}")
        logger.info(f"Distribution Profile Name: {dist_profile}")
        logger.info(f"Email: {email}")

    if not dist_profile_id and not dist_profile:
        raise click.UsageError("Either --distProfileId or --distProfile is required.")

    try:
        result = add_tester_to_distribution_profile(
            dist_profile_id or dist_profile, email
        )
        click.echo(json.dumps(result, indent=2))
    except Exception as e:
        if ctx.obj["debug"]:
            logger.error(f"An error occurred: {e}", exc_info=True)
        else:
            click.echo(f"Error: {e}", err=True)


@profile_settings.command(name="remove-tester")
@click.option(
    "--distProfileId", "dist_profile_id", help="Distribution Profile ID (UUID format)"
)
@click.option(
    "--distProfile",
    "dist_profile",
    help="Distribution Profile Name instead of 'distProfileId'",
)
@click.option("--email", required=True, help="Tester Email Address")
@click.pass_context
def profile_remove_tester(ctx, dist_profile_id, dist_profile, email):
    """Remove Tester from Distribution Profile"""
    if ctx.obj["debug"]:
        logger.info(
            "Removing a tester from a distribution profile with the following parameters:"
        )
        logger.info(f"Distribution Profile ID: {dist_profile_id}")
        logger.info(f"Distribution Profile Name: {dist_profile}")
        logger.info(f"Email: {email}")

    if not dist_profile_id and not dist_profile:
        raise click.UsageError("Either --distProfileId or --distProfile is required.")

    try:
        result = remove_tester_from_distribution_profile(
            dist_profile_id or dist_profile, email
        )
        click.echo(json.dumps(result, indent=2))
    except Exception as e:
        if ctx.obj["debug"]:
            logger.error(f"An error occurred: {e}", exc_info=True)
        else:
            click.echo(f"Error: {e}", err=True)


@profile_settings.command(name="add-group")
@click.option(
    "--distProfileId", "dist_profile_id", help="Distribution Profile ID (UUID format)"
)
@click.option(
    "--distProfile",
    "dist_profile",
    help="Distribution Profile Name instead of 'distProfileId'",
)
@click.option(
    "--testingGroupId", "testing_group_id", required=True, help="Testing Group ID"
)
@click.pass_context
def profile_add_group(ctx, dist_profile_id, dist_profile, testing_group_id):
    """Add Testing Group to Distribution Profile"""
    if ctx.obj["debug"]:
        logger.info(
            "Adding a testing group to a distribution profile with the following parameters:"
        )
        logger.info(f"Distribution Profile ID: {dist_profile_id}")
        logger.info(f"Distribution Profile Name: {dist_profile}")
        logger.info(f"Testing Group ID: {testing_group_id}")

    if not dist_profile_id and not dist_profile:
        raise click.UsageError("Either --distProfileId or --distProfile is required.")

    try:
        result = add_testing_group_to_distribution_profile(
            dist_profile_id or dist_profile, testing_group_id
        )
        click.echo(json.dumps(result, indent=2))
    except Exception as e:
        if ctx.obj["debug"]:
            logger.error(f"An error occurred: {e}", exc_info=True)
        else:
            click.echo(f"Error: {e}", err=True)


@profile_settings.command(name="remove-group")
@click.option(
    "--distProfileId", "dist_profile_id", help="Distribution Profile ID (UUID format)"
)
@click.option(
    "--distProfile",
    "dist_profile",
    help="Distribution Profile Name instead of 'distProfileId'",
)
@click.option(
    "--testingGroupId", "testing_group_id", required=True, help="Testing Group ID"
)
@click.pass_context
def profile_remove_group(ctx, dist_profile_id, dist_profile, testing_group_id):
    """Remove Testing Group from Distribution Profile"""
    if ctx.obj["debug"]:
        logger.info(
            "Removing a testing group from a distribution profile with the following parameters:"
        )
        logger.info(f"Distribution Profile ID: {dist_profile_id}")
        logger.info(f"Distribution Profile Name: {dist_profile}")
        logger.info(f"Testing Group ID: {testing_group_id}")

    if not dist_profile_id and not dist_profile:
        raise click.UsageError("Either --distProfileId or --distProfile is required.")

    try:
        result = remove_testing_group_from_distribution_profile(
            dist_profile_id or dist_profile, testing_group_id
        )
        click.echo(json.dumps(result, indent=2))
    except Exception as e:
        if ctx.obj["debug"]:
            logger.error(f"An error occurred: {e}", exc_info=True)
        else:
            click.echo(f"Error: {e}", err=True)


@profile_settings.command(name="add-workflow")
@click.option(
    "--distProfileId", "dist_profile_id", help="Distribution Profile ID (UUID format)"
)
@click.option(
    "--distProfile",
    "dist_profile",
    help="Distribution Profile Name instead of 'distProfileId'",
)
@click.option("--workflowId", "workflow_id", required=True, help="Workflow ID")
@click.pass_context
def profile_add_workflow(ctx, dist_profile_id, dist_profile, workflow_id):
    """Add Workflow to Distribution Profile"""
    if ctx.obj["debug"]:
        logger.info(
            "Adding a workflow to a distribution profile with the following parameters:"
        )
        logger.info(f"Distribution Profile ID: {dist_profile_id}")
        logger.info(f"Distribution Profile Name: {dist_profile}")
        logger.info(f"Workflow ID: {workflow_id}")

    if not dist_profile_id and not dist_profile:
        raise click.UsageError("Either --distProfileId or --distProfile is required.")

    try:
        result = add_workflow_to_distribution_profile(
            dist_profile_id or dist_profile, workflow_id
        )
        click.echo(json.dumps(result, indent=2))
    except Exception as e:
        if ctx.obj["debug"]:
            logger.error(f"An error occurred: {e}", exc_info=True)
        else:
            click.echo(f"Error: {e}", err=True)


@profile_settings.command(name="remove-workflow")
@click.option(
    "--distProfileId", "dist_profile_id", help="Distribution Profile ID (UUID format)"
)
@click.option(
    "--distProfile",
    "dist_profile",
    help="Distribution Profile Name instead of 'distProfileId'",
)
@click.option("--workflowId", "workflow_id", required=True, help="Workflow ID")
@click.pass_context
def profile_remove_workflow(ctx, dist_profile_id, dist_profile, workflow_id):
    """Remove Workflow from Distribution Profile"""
    if ctx.obj["debug"]:
        logger.info(
            "Removing a workflow from a distribution profile with the following parameters:"
        )
        logger.info(f"Distribution Profile ID: {dist_profile_id}")
        logger.info(f"Distribution Profile Name: {dist_profile}")
        logger.info(f"Workflow ID: {workflow_id}")

    if not dist_profile_id and not dist_profile:
        raise click.UsageError("Either --distProfileId or --distProfile is required.")

    try:
        result = remove_workflow_from_distribution_profile(
            dist_profile_id or dist_profile, workflow_id
        )
        click.echo(json.dumps(result, indent=2))
    except Exception as e:
        if ctx.obj["debug"]:
            logger.error(f"An error occurred: {e}", exc_info=True)
        else:
            click.echo(f"Error: {e}", err=True)
