import click
import json
import logging
from .api import (
    get_build_profiles,
    get_branches,
    get_commits,
    get_workflows,
    get_configurations,
    start_build,
    get_active_builds,
    get_builds,
    get_build,
    download_artifacts,
    download_log as download_log_api,
    get_variable_groups,
    create_variable_group,
    upload_build_variables_from_file,
    download_variables,
    create_variable,
    get_variables,
    get_variable_group_details,
    create_build_configuration,
    update_build_configuration,
    delete_build_configuration,
    get_build_configuration_details,
)
from .utils import (
    resolve_profile_name_to_id,
    resolve_branch_name_to_id,
    resolve_workflow_name_to_id,
    resolve_configuration_name_to_id,
    auto_resolve_configuration_id,
    auto_resolve_latest_commit_id,
    resolve_commit_hash_to_id,
    setup_debug_mode,
)

logger = logging.getLogger(__name__)


@click.group()
def build():
    """Manage Build Actions"""
    pass


@click.group()
def profile():
    """Manage Build Profiles"""
    pass


@click.group()
def branch():
    """Manage Branches"""
    pass


@click.group()
def variable():
    """Manage Environment Variables"""
    pass


@click.group()
def group():
    """Manage Environment Variable Groups"""
    pass


@click.group()
def configuration():
    """Manage Build Configurations"""
    pass


build.add_command(profile)
profile.add_command(branch)
profile.add_command(configuration)
build.add_command(variable)
variable.add_command(group)


@build.command()
@click.option("--profileId", "profile_id", help="Build Profile ID (UUID format)")
@click.option("--profile", help="Build Profile Name instead of 'profileId'")
@click.option(
    "--branchId",
    "branch_id",
    help="Branch ID (UUID format, required unless using --branch)",
)
@click.option("--branch", help="Branch Name instead of 'branchId'")
@click.option("--commitId", "commit_id", help="Commit ID (UUID format, optional)")
@click.option(
    "--commitHash", "commit_hash", help="Commit hash (alternative to --commitId)"
)
@click.option(
    "--configurationId",
    "configuration_id",
    help="Configuration ID (UUID format, optional)",
)
@click.option(
    "--configuration", help="Configuration name (alternative to --configurationId)"
)
@click.option(
    "--workflowId",
    "workflow_id",
    help="Workflow ID (UUID format, required unless using --workflow)",
)
@click.option("--workflow", help="Workflow Name instead of 'workflowId'")
@click.option("--debug", is_flag=True, help="Enable debug mode with verbose output")
@click.pass_context
def start(
    ctx,
    profile_id,
    profile,
    branch_id,
    branch,
    commit_id,
    commit_hash,
    configuration_id,
    configuration,
    workflow_id,
    workflow,
    debug,
):
    """Start a New Build"""
    debug_enabled = setup_debug_mode(ctx, debug)
    
    if debug_enabled:
        logger.info("Starting a new build with the following parameters:")
        logger.info(f"Profile ID: {profile_id}")
        logger.info(f"Profile Name: {profile}")
        logger.info(f"Branch ID: {branch_id}")
        logger.info(f"Branch Name: {branch}")
        logger.info(f"Commit ID: {commit_id}")
        logger.info(f"Commit Hash: {commit_hash}")
        logger.info(f"Configuration ID: {configuration_id}")
        logger.info(f"Configuration Name: {configuration}")
        logger.info(f"Workflow ID: {workflow_id}")
        logger.info(f"Workflow Name: {workflow}")

    if not profile_id and not profile:
        raise click.UsageError("Either --profileId or --profile is required.")
    if not branch_id and not branch:
        raise click.UsageError("Either --branchId or --branch is required.")
    if not workflow_id and not workflow:
        raise click.UsageError("Either --workflowId or --workflow is required.")

    try:
        profile_input = profile_id or profile
        branch_input = branch_id or branch
        workflow_input = workflow_id or workflow

        resolved_profile_id = resolve_profile_name_to_id(profile_input)
        resolved_branch_id = resolve_branch_name_to_id(
            resolved_profile_id, branch_input
        )
        resolved_workflow_id = resolve_workflow_name_to_id(
            resolved_profile_id, workflow_input
        )

        if configuration_id:
            resolved_configuration_id = configuration_id
        elif configuration:
            resolved_configuration_id = resolve_configuration_name_to_id(
                resolved_profile_id, configuration
            )
        else:
            resolved_configuration_id = auto_resolve_configuration_id(
                resolved_profile_id
            )

        if commit_id:
            resolved_commit_id = commit_id
        elif commit_hash:
            resolved_commit_id = resolve_commit_hash_to_id(
                resolved_profile_id, resolved_branch_id, commit_hash
            )
        else:
            resolved_commit_id = auto_resolve_latest_commit_id(
                resolved_profile_id, resolved_branch_id
            )

        result = start_build(
            {
                "workflowId": resolved_workflow_id,
                "configurationId": resolved_configuration_id,
                "commitId": resolved_commit_id,
            }
        )
        click.echo(json.dumps(result, indent=2))

    except Exception as e:
        if debug_enabled:
            logger.error(f"An error occurred: {e}", exc_info=True)
        else:
            click.echo(f"Error: {e}", err=True)


@build.command(name="active-list")
@click.option("--debug", is_flag=True, help="Enable debug mode with verbose output")
@click.pass_context
def active_list(ctx, debug):
    """Get a List of Active Builds in the Queue"""
    debug_enabled = setup_debug_mode(ctx, debug)
    
    if debug_enabled:
        logger.info("Fetching active builds.")

    try:
        builds = get_active_builds()
        click.echo(json.dumps(builds, indent=2))
    except Exception as e:
        if debug_enabled:
            logger.error(f"An error occurred: {e}", exc_info=True)
        else:
            click.echo(f"Error: {e}", err=True)


@build.command(name="list")
@click.option("--profileId", "profile_id", help="Build profile ID (UUID format)")
@click.option("--profile", help="Build profile name (alternative to --profileId)")
@click.option("--branchId", "branch_id", help="Branch ID (UUID format)")
@click.option("--branch", help="Branch name (alternative to --branchId)")
@click.option("--commitId", "commit_id", required=True, help="Commit ID (UUID format)")
@click.option("--debug", is_flag=True, help="Enable debug mode with verbose output")
@click.pass_context
def list_(ctx, profile_id, profile, branch_id, branch, commit_id, debug):
    """Get List of Builds of a Commit"""
    debug_enabled = setup_debug_mode(ctx, debug)
    
    if debug_enabled:
        logger.info("Fetching builds with the following parameters:")
        logger.info(f"Profile ID: {profile_id}")
        logger.info(f"Profile Name: {profile}")
        logger.info(f"Branch ID: {branch_id}")
        logger.info(f"Branch Name: {branch}")
        logger.info(f"Commit ID: {commit_id}")

    if not profile_id and not profile:
        raise click.UsageError("Either --profileId or --profile is required.")
    if not branch_id and not branch:
        raise click.UsageError("Either --branchId or --branch is required.")

    try:
        builds = get_builds(profile_id, branch_id, commit_id)
        click.echo(json.dumps(builds, indent=2))
    except Exception as e:
        if debug_enabled:
            logger.error(f"An error occurred: {e}", exc_info=True)
        else:
            click.echo(f"Error: {e}", err=True)


@build.command(name="view")
@click.option("--profileId", "profile_id", help="Build profile ID (UUID format)")
@click.option("--profile", help="Build profile name (alternative to --profileId)")
@click.option("--branchId", "branch_id", help="Branch ID (UUID format)")
@click.option("--branch", help="Branch name (alternative to --branchId)")
@click.option("--commitId", "commit_id", required=True, help="Commit ID (UUID format)")
@click.option("--buildId", "build_id", required=True, help="Build ID (UUID format)")
@click.pass_context
def view(ctx, profile_id, profile, branch_id, branch, commit_id, build_id):
    """View Details of a Build"""
    if ctx.obj["debug"]:
        logger.info("Fetching build details with the following parameters:")
        logger.info(f"Profile ID: {profile_id}")
        logger.info(f"Profile Name: {profile}")
        logger.info(f"Branch ID: {branch_id}")
        logger.info(f"Branch Name: {branch}")
        logger.info(f"Commit ID: {commit_id}")
        logger.info(f"Build ID: {build_id}")

    if not profile_id and not profile:
        raise click.UsageError("Either --profileId or --profile is required.")
    if not branch_id and not branch:
        raise click.UsageError("Either --branchId or --branch is required.")

    try:
        build = get_build(profile_id, branch_id, commit_id, build_id)
        click.echo(json.dumps(build, indent=2))
    except Exception as e:
        if ctx.obj["debug"]:
            logger.error(f"An error occurred: {e}", exc_info=True)
        else:
            click.echo(f"Error: {e}", err=True)


@build.command(name="download")
@click.option("--profileId", "profile_id", help="Build profile ID (UUID format)")
@click.option("--profile", help="Build profile name (alternative to --profileId)")
@click.option("--branchId", "branch_id", help="Branch ID (UUID format)")
@click.option("--branch", help="Branch name (alternative to --branchId)")
@click.option("--commitId", "commit_id", required=True, help="Commit ID (UUID format)")
@click.option("--buildId", "build_id", required=True, help="Build ID (UUID format)")
@click.option("--path", required=False, help="The Path for artifacts to be downloaded")
@click.pass_context
def download(ctx, profile_id, profile, branch_id, branch, commit_id, build_id, path):
    """Download Artifacts"""
    if ctx.obj["debug"]:
        logger.info("Downloading artifacts with the following parameters:")
        logger.info(f"Profile ID: {profile_id}")
        logger.info(f"Profile Name: {profile}")
        logger.info(f"Branch ID: {branch_id}")
        logger.info(f"Branch Name: {branch}")
        logger.info(f"Commit ID: {commit_id}")
        logger.info(f"Build ID: {build_id}")
        logger.info(f"Path: {path}")

    if not profile_id and not profile:
        raise click.UsageError("Either --profileId or --profile is required.")
    if not branch_id and not branch:
        raise click.UsageError("Either --branchId or --branch is required.")

    try:
        download_artifacts(profile_id, branch_id, commit_id, build_id, path)
    except Exception as e:
        if ctx.obj["debug"]:
            logger.error(f"An error occurred: {e}", exc_info=True)
        else:
            click.echo(f"Error: {e}", err=True)


@build.command(name="download-log")
@click.option("--profileId", "profile_id", help="Build profile ID (UUID format)")
@click.option("--profile", help="Build profile name (alternative to --profileId)")
@click.option("--branchId", "branch_id", help="Branch ID (UUID format)")
@click.option("--branch", help="Branch name (alternative to --branchId)")
@click.option("--commitId", "commit_id", required=True, help="Commit ID (UUID format)")
@click.option("--buildId", "build_id", required=True, help="Build ID (UUID format)")
@click.option("--path", required=False, help="The Path for log to be downloaded")
@click.pass_context
def download_log(
    ctx, profile_id, profile, branch_id, branch, commit_id, build_id, path
):
    """Download Build Logs"""
    if ctx.obj["debug"]:
        logger.info("Downloading build logs with the following parameters:")
        logger.info(f"Profile ID: {profile_id}")
        logger.info(f"Profile Name: {profile}")
        logger.info(f"Branch ID: {branch_id}")
        logger.info(f"Branch Name: {branch}")
        logger.info(f"Commit ID: {commit_id}")
        logger.info(f"Build ID: {build_id}")
        logger.info(f"Path: {path}")

    if not profile_id and not profile:
        raise click.UsageError("Either --profileId or --profile is required.")
    if not branch_id and not branch:
        raise click.UsageError("Either --branchId or --branch is required.")

    try:
        download_log_api(profile_id, branch_id, commit_id, build_id, path)
    except Exception as e:
        if ctx.obj["debug"]:
            logger.error(f"An error occurred: {e}", exc_info=True)
        else:
            click.echo(f"Error: {e}", err=True)


@profile.command(name="list")
@click.pass_context
def profile_list(ctx):
    """Get List of Build Profiles"""
    if ctx.obj["debug"]:
        logger.info("Fetching build profiles.")

    try:
        profiles = get_build_profiles()
        click.echo(json.dumps(profiles, indent=2))
    except Exception as e:
        if ctx.obj["debug"]:
            logger.error(f"An error occurred: {e}", exc_info=True)
        else:
            click.echo(f"Error: {e}", err=True)


@branch.command(name="list")
@click.option("--profileId", "profile_id", help="Build Profile ID")
@click.option("--profile", help="Build Profile Name instead of 'profileId'")
@click.pass_context
def branch_list(ctx, profile_id, profile):
    """Get List of Branches of a Build Profile"""
    if ctx.obj["debug"]:
        logger.info("Fetching branches with the following parameters:")
        logger.info(f"Profile ID: {profile_id}")
        logger.info(f"Profile Name: {profile}")

    if not profile_id and not profile:
        raise click.UsageError("Either --profileId or --profile is required.")

    try:
        resolved_profile_id = resolve_profile_name_to_id(profile_id or profile)
        branches = get_branches(resolved_profile_id)
        click.echo(json.dumps(branches, indent=2))
    except Exception as e:
        if ctx.obj["debug"]:
            logger.error(f"An error occurred: {e}", exc_info=True)
        else:
            click.echo(f"Error: {e}", err=True)


@branch.command(name="commits")
@click.option("--profileId", "profile_id", help="Build Profile ID")
@click.option("--profile", help="Build Profile Name instead of 'profileId'")
@click.option("--branchId", "branch_id", help="Branch ID")
@click.option("--branch", help="Branch Name instead of 'branchId'")
@click.pass_context
def commits(ctx, profile_id, profile, branch_id, branch):
    """Get List of Commits of a Branch"""
    if ctx.obj["debug"]:
        logger.info("Fetching commits with the following parameters:")
        logger.info(f"Profile ID: {profile_id}")
        logger.info(f"Profile Name: {profile}")
        logger.info(f"Branch ID: {branch_id}")
        logger.info(f"Branch Name: {branch}")

    if not profile_id and not profile:
        raise click.UsageError("Either --profileId or --profile is required.")
    if not branch_id and not branch:
        raise click.UsageError("Either --branchId or --branch is required.")

    try:
        commits = get_commits(profile_id or profile, branch_id or branch)
        click.echo(json.dumps(commits, indent=2))
    except Exception as e:
        if ctx.obj["debug"]:
            logger.error(f"An error occurred: {e}", exc_info=True)
        else:
            click.echo(f"Error: {e}", err=True)


@profile.command(name="workflows")
@click.option("--profileId", "profile_id", help="Build Profile ID")
@click.option("--profile", help="Build Profile Name instead of 'profileId'")
@click.pass_context
def workflows(ctx, profile_id, profile):
    """Get List of Workflows of a Build Profile"""
    if ctx.obj["debug"]:
        logger.info("Fetching workflows with the following parameters:")
        logger.info(f"Profile ID: {profile_id}")
        logger.info(f"Profile Name: {profile}")

    if not profile_id and not profile:
        raise click.UsageError("Either --profileId or --profile is required.")

    try:
        workflows = get_workflows(profile_id or profile)
        click.echo(json.dumps(workflows, indent=2))
    except Exception as e:
        if ctx.obj["debug"]:
            logger.error(f"An error occurred: {e}", exc_info=True)
        else:
            click.echo(f"Error: {e}", err=True)


@profile.command(name="configurations")
@click.option("--profileId", "profile_id", help="Build Profile ID")
@click.option("--profile", help="Build Profile Name instead of 'profileId'")
@click.pass_context
def configurations(ctx, profile_id, profile):
    """Get List of Configurations of a Build Profile"""
    if ctx.obj["debug"]:
        logger.info("Fetching configurations with the following parameters:")
        logger.info(f"Profile ID: {profile_id}")
        logger.info(f"Profile Name: {profile}")

    if not profile_id and not profile:
        raise click.UsageError("Either --profileId or --profile is required.")

    try:
        resolved_profile_id = resolve_profile_name_to_id(profile_id or profile)
        configurations = get_configurations(resolved_profile_id)
        click.echo(json.dumps(configurations, indent=2))
    except Exception as e:
        if ctx.obj["debug"]:
            logger.error(f"An error occurred: {e}", exc_info=True)
        else:
            click.echo(f"Error: {e}", err=True)


@configuration.command(name="list")
@click.option("--profileId", "profile_id", help="Build Profile ID")
@click.option("--profile", help="Build Profile Name instead of 'profileId'")
@click.pass_context
def configuration_list(ctx, profile_id, profile):
    """Get List of Configurations of a Build Profile"""
    if ctx.obj["debug"]:
        logger.info("Fetching configurations with the following parameters:")
        logger.info(f"Profile ID: {profile_id}")
        logger.info(f"Profile Name: {profile}")

    if not profile_id and not profile:
        raise click.UsageError("Either --profileId or --profile is required.")

    try:
        resolved_profile_id = resolve_profile_name_to_id(profile_id or profile)
        configurations = get_configurations(resolved_profile_id)
        click.echo(json.dumps(configurations, indent=2))
    except Exception as e:
        if ctx.obj["debug"]:
            logger.error(f"An error occurred: {e}", exc_info=True)
        else:
            click.echo(f"Error: {e}", err=True)


@configuration.command(name="view")
@click.option("--profileId", "profile_id", help="Build Profile ID")
@click.option("--profile", help="Build Profile Name instead of 'profileId'")
@click.option(
    "--configurationId", "configuration_id", required=True, help="Configuration ID"
)
@click.pass_context
def configuration_view(ctx, profile_id, profile, configuration_id):
    """View Details of a Build Configuration"""
    if ctx.obj["debug"]:
        logger.info(
            "Fetching build configuration details with the following parameters:"
        )
        logger.info(f"Profile ID: {profile_id}")
        logger.info(f"Profile Name: {profile}")
        logger.info(f"Configuration ID: {configuration_id}")

    if not profile_id and not profile:
        raise click.UsageError("Either --profileId or --profile is required.")

    try:
        resolved_profile_id = resolve_profile_name_to_id(profile_id or profile)
        configuration = get_build_configuration_details(
            resolved_profile_id, configuration_id
        )
        click.echo(json.dumps(configuration, indent=2))
    except Exception as e:
        if ctx.obj["debug"]:
            logger.error(f"An error occurred: {e}", exc_info=True)
        else:
            click.echo(f"Error: {e}", err=True)


@configuration.command(name="create")
@click.option("--profileId", "profile_id", help="Build Profile ID")
@click.option("--profile", help="Build Profile Name instead of 'profileId'")
@click.option("--name", required=True, help="Configuration name")
@click.option("--data", help="Configuration data as JSON string")
@click.pass_context
def configuration_create(ctx, profile_id, profile, name, data):
    """Create New Build Configuration"""
    if ctx.obj["debug"]:
        logger.info("Creating a new build configuration with the following parameters:")
        logger.info(f"Profile ID: {profile_id}")
        logger.info(f"Profile Name: {profile}")
        logger.info(f"Name: {name}")
        logger.info(f"Data: {data}")

    if not profile_id and not profile:
        raise click.UsageError("Either --profileId or --profile is required.")

    try:
        resolved_profile_id = resolve_profile_name_to_id(profile_id or profile)
        config_data = {"name": name}
        if data:
            import json as json_lib

            config_data.update(json_lib.loads(data))

        result = create_build_configuration(resolved_profile_id, config_data)
        click.echo(json.dumps(result, indent=2))
    except Exception as e:
        if ctx.obj["debug"]:
            logger.error(f"An error occurred: {e}", exc_info=True)
        else:
            click.echo(f"Error: {e}", err=True)


@configuration.command(name="update")
@click.option("--profileId", "profile_id", help="Build Profile ID")
@click.option("--profile", help="Build Profile Name instead of 'profileId'")
@click.option(
    "--configurationId", "configuration_id", required=True, help="Configuration ID"
)
@click.option("--data", required=True, help="Configuration data as JSON string")
@click.pass_context
def configuration_update(ctx, profile_id, profile, configuration_id, data):
    """Update Build Configuration"""
    if ctx.obj["debug"]:
        logger.info("Updating a build configuration with the following parameters:")
        logger.info(f"Profile ID: {profile_id}")
        logger.info(f"Profile Name: {profile}")
        logger.info(f"Configuration ID: {configuration_id}")
        logger.info(f"Data: {data}")

    if not profile_id and not profile:
        raise click.UsageError("Either --profileId or --profile is required.")

    try:
        resolved_profile_id = resolve_profile_name_to_id(profile_id or profile)
        import json as json_lib

        config_data = json_lib.loads(data)

        result = update_build_configuration(
            resolved_profile_id, configuration_id, config_data
        )
        click.echo(json.dumps(result, indent=2))
    except Exception as e:
        if ctx.obj["debug"]:
            logger.error(f"An error occurred: {e}", exc_info=True)
        else:
            click.echo(f"Error: {e}", err=True)


@configuration.command(name="delete")
@click.option("--profileId", "profile_id", help="Build Profile ID")
@click.option("--profile", help="Build Profile Name instead of 'profileId'")
@click.option(
    "--configurationId", "configuration_id", required=True, help="Configuration ID"
)
@click.pass_context
def configuration_delete(ctx, profile_id, profile, configuration_id):
    """Delete Build Configuration"""
    if ctx.obj["debug"]:
        logger.info("Deleting a build configuration with the following parameters:")
        logger.info(f"Profile ID: {profile_id}")
        logger.info(f"Profile Name: {profile}")
        logger.info(f"Configuration ID: {configuration_id}")

    if not profile_id and not profile:
        raise click.UsageError("Either --profileId or --profile is required.")

    try:
        resolved_profile_id = resolve_profile_name_to_id(profile_id or profile)
        result = delete_build_configuration(resolved_profile_id, configuration_id)
        click.echo(json.dumps(result, indent=2))
    except Exception as e:
        if ctx.obj["debug"]:
            logger.error(f"An error occurred: {e}", exc_info=True)
        else:
            click.echo(f"Error: {e}", err=True)


@group.command(name="list")
@click.pass_context
def group_list(ctx):
    """List Groups"""
    if ctx.obj["debug"]:
        logger.info("Fetching variable groups.")

    try:
        groups = get_variable_groups()
        click.echo(json.dumps(groups, indent=2))
    except Exception as e:
        if ctx.obj["debug"]:
            logger.error(f"An error occurred: {e}", exc_info=True)
        else:
            click.echo(f"Error: {e}", err=True)


@group.command(name="create")
@click.option("--name", required=True, help="Variable Group Name")
@click.pass_context
def group_create(ctx, name):
    """Create an Environment Variable Group"""
    if ctx.obj["debug"]:
        logger.info(f"Creating a new variable group with name: {name}")

    try:
        group = create_variable_group(name)
        click.echo(json.dumps(group, indent=2))
    except Exception as e:
        if ctx.obj["debug"]:
            logger.error(f"An error occurred: {e}", exc_info=True)
        else:
            click.echo(f"Error: {e}", err=True)


@group.command(name="upload")
@click.option("--variableGroupId", "variable_group_id", help="Variable Group ID")
@click.option(
    "--variableGroup",
    "variable_group",
    help="Variable Group Name instead of 'variableGroupId'",
)
@click.option("--filePath", "file_path", required=True, help="JSON File Path")
@click.pass_context
def group_upload(ctx, variable_group_id, variable_group, file_path):
    """Upload Environment Variables from JSON File"""
    if ctx.obj["debug"]:
        logger.info("Uploading environment variables with the following parameters:")
        logger.info(f"Variable Group ID: {variable_group_id}")
        logger.info(f"Variable Group Name: {variable_group}")
        logger.info(f"File Path: {file_path}")

    if not variable_group_id and not variable_group:
        raise click.UsageError(
            "Either --variableGroupId or --variableGroup is required."
        )

    try:
        result = upload_build_variables_from_file(
            variable_group_id or variable_group, file_path
        )
        click.echo(json.dumps(result, indent=2))
    except Exception as e:
        if ctx.obj["debug"]:
            logger.error(f"An error occurred: {e}", exc_info=True)
        else:
            click.echo(f"An error occurred: {e}", err=True)


@group.command(name="download")
@click.option("--variableGroupId", "variable_group_id", help="Variable Group ID")
@click.option(
    "--variableGroup",
    "variable_group",
    help="Variable Group Name instead of 'variableGroupId'",
)
@click.option("--path", required=False, help="The Path for JSON file to be downloaded")
@click.pass_context
def group_download(ctx, variable_group_id, variable_group, path):
    """Download Environment Variables as JSON"""
    if ctx.obj["debug"]:
        logger.info("Downloading environment variables with the following parameters:")
        logger.info(f"Variable Group ID: {variable_group_id}")
        logger.info(f"Variable Group Name: {variable_group}")
        logger.info(f"Path: {path}")

    if not variable_group_id and not variable_group:
        raise click.UsageError(
            "Either --variableGroupId or --variableGroup is required."
        )

    try:
        download_variables(variable_group_id or variable_group, path)
    except Exception as e:
        if ctx.obj["debug"]:
            logger.error(f"An error occurred: {e}", exc_info=True)
        else:
            click.echo(f"Error: {e}", err=True)


@group.command(name="view")
@click.option("--variableGroupId", "variable_group_id", help="Variable Group ID")
@click.option(
    "--variableGroup",
    "variable_group",
    help="Variable Group Name instead of 'variableGroupId'",
)
@click.pass_context
def group_view(ctx, variable_group_id, variable_group):
    """View Details of a Variable Group"""
    if ctx.obj["debug"]:
        logger.info("Fetching variable group details with the following parameters:")
        logger.info(f"Variable Group ID: {variable_group_id}")
        logger.info(f"Variable Group Name: {variable_group}")

    if not variable_group_id and not variable_group:
        raise click.UsageError(
            "Either --variableGroupId or --variableGroup is required."
        )

    try:
        group_details = get_variable_group_details(variable_group_id or variable_group)
        click.echo(json.dumps(group_details, indent=2))
    except Exception as e:
        if ctx.obj["debug"]:
            logger.error(f"An error occurred: {e}", exc_info=True)
        else:
            click.echo(f"Error: {e}", err=True)


@variable.command(name="create")
@click.option("--variableGroupId", "variable_group_id", help="Variable Group ID")
@click.option(
    "--variableGroup",
    "variable_group",
    help="Variable Group Name instead of 'variableGroupId'",
)
@click.option(
    "--type",
    "type_",
    required=True,
    type=click.Choice(["text", "file"]),
    help="Variable type",
)
@click.option("--key", required=True, help="Variable key name")
@click.option("--value", help="Variable value (required for text type)")
@click.option("--filePath", "file_path", help="File path (required for file type)")
@click.option("--isSecret", "is_secret", is_flag=True, help="Mark variable as secret")
@click.pass_context
def create(
    ctx, variable_group_id, variable_group, type_, key, value, file_path, is_secret
):
    """Create a File or Text Environment Variable"""
    if ctx.obj["debug"]:
        logger.info(
            "Creating a new environment variable with the following parameters:"
        )
        logger.info(f"Variable Group ID: {variable_group_id}")
        logger.info(f"Variable Group Name: {variable_group}")
        logger.info(f"Type: {type_}")
        logger.info(f"Key: {key}")
        logger.info(f"Value: {value}")
        logger.info(f"File Path: {file_path}")
        logger.info(f"Is Secret: {is_secret}")

    if not variable_group_id and not variable_group:
        raise click.UsageError(
            "Either --variableGroupId or --variableGroup is required."
        )

    data = {"key": key, "isSecret": is_secret}
    if type_ == "text":
        if not value:
            click.echo("Error: --value is required for text type variables.", err=True)
            return
        data["value"] = value
    elif type_ == "file":
        if not file_path:
            click.echo(
                "Error: --filePath is required for file type variables.", err=True
            )
            return
        with open(file_path, "rb") as f:
            data["value"] = f.read()

    try:
        result = create_variable(variable_group_id or variable_group, data)
        click.echo(json.dumps(result, indent=2))
    except Exception as e:
        if ctx.obj["debug"]:
            logger.error(f"An error occurred: {e}", exc_info=True)
        else:
            click.echo(f"Error: {e}", err=True)


@variable.command(name="view")
@click.option("--variableGroupId", "variable_group_id", help="Variable Group ID")
@click.option(
    "--variableGroup",
    "variable_group",
    help="Variable Group Name instead of 'variableGroupId'",
)
@click.pass_context
def variable_view(ctx, variable_group_id, variable_group):
    """Get List of Environment Variables"""
    if ctx.obj["debug"]:
        logger.info("Fetching environment variables with the following parameters:")
        logger.info(f"Variable Group ID: {variable_group_id}")
        logger.info(f"Variable Group Name: {variable_group}")

    if not variable_group_id and not variable_group:
        raise click.UsageError(
            "Either --variableGroupId or --variableGroup is required."
        )

    try:
        variables = get_variables(variable_group_id or variable_group)
        click.echo(json.dumps(variables, indent=2))
    except Exception as e:
        if ctx.obj["debug"]:
            logger.error(f"An error occurred: {e}", exc_info=True)
        else:
            click.echo(f"Error: {e}", err=True)
