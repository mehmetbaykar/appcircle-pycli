import logging
import click
from typing import Optional
from .api import get_build_profiles
from .api import get_branches
from .api import get_workflows
from .api import get_configurations
from .api import get_commits

logger = logging.getLogger(__name__)


def setup_debug_mode(ctx, debug_flag_value=None):
    """Setup debug mode if enabled either globally or locally"""
    if ctx.obj and ctx.obj.get("debug"):
        return True
    
    if debug_flag_value:
        ctx.ensure_object(dict)
        ctx.obj["debug"] = True
        
        logging.basicConfig(level=logging.DEBUG, force=True)
        click.echo("Debug mode enabled", err=True)
        return True
    
    return False


def is_uuid_format(value: str) -> bool:
    """Check if a string looks like a UUID format."""
    return isinstance(value, str) and "-" in value and len(value) == 36


def resolve_profile_name_to_id(profile_name_or_id: Optional[str]) -> str:
    if not profile_name_or_id:
        raise Exception("Profile name or ID is required")

    if is_uuid_format(profile_name_or_id):
        return profile_name_or_id

    logger.debug(f"Resolving profile name '{profile_name_or_id}' to ID")
    profiles = get_build_profiles()
    found_profile = next(
        (p for p in profiles if p.get("name") == profile_name_or_id), None
    )
    if not found_profile:
        raise Exception(f"Build profile '{profile_name_or_id}' not found.")

    profile_id = found_profile["id"]
    logger.debug(f"Resolved profile '{profile_name_or_id}' to ID: {profile_id}")
    return profile_id


def resolve_branch_name_to_id(profile_id: str, branch_name_or_id: Optional[str]) -> str:
    if not branch_name_or_id:
        raise Exception("Branch name or ID is required")

    if is_uuid_format(branch_name_or_id):
        return branch_name_or_id

    logger.debug(f"Resolving branch name '{branch_name_or_id}' to ID")
    profile_data = get_branches(profile_id)
    found_branch = next(
        (
            b
            for b in profile_data.get("branches", [])
            if b.get("name") == branch_name_or_id
        ),
        None,
    )
    if not found_branch:
        raise Exception(f"Branch '{branch_name_or_id}' not found for build profile.")

    branch_id = found_branch["id"]
    logger.debug(f"Resolved branch '{branch_name_or_id}' to ID: {branch_id}")
    return branch_id


def resolve_workflow_name_to_id(
    profile_id: str, workflow_name_or_id: Optional[str]
) -> str:
    if not workflow_name_or_id:
        raise Exception("Workflow name or ID is required")

    if is_uuid_format(workflow_name_or_id):
        return workflow_name_or_id

    logger.debug(f"Resolving workflow name '{workflow_name_or_id}' to ID")
    workflows = get_workflows(profile_id)
    found_workflow = next(
        (w for w in workflows if w.get("workflowName") == workflow_name_or_id), None
    )
    if not found_workflow:
        raise Exception(
            f"Workflow '{workflow_name_or_id}' not found for build profile."
        )

    workflow_id = found_workflow["id"]
    logger.debug(f"Resolved workflow '{workflow_name_or_id}' to ID: {workflow_id}")
    return workflow_id


def resolve_configuration_name_to_id(
    profile_id: str, configuration_name_or_id: Optional[str]
) -> Optional[str]:
    if not configuration_name_or_id:
        return None

    if is_uuid_format(configuration_name_or_id):
        return configuration_name_or_id

    logger.debug(f"Resolving configuration name '{configuration_name_or_id}' to ID")
    configurations = get_configurations(profile_id)
    found_config = next(
        (
            c
            for c in configurations
            if c.get("item1", {}).get("configurationName") == configuration_name_or_id
        ),
        None,
    )
    if not found_config:
        raise Exception(
            f"Configuration '{configuration_name_or_id}' not found for build profile."
        )

    configuration_id = found_config["item1"]["id"]
    logger.debug(
        f"Resolved configuration '{configuration_name_or_id}' to ID: {configuration_id}"
    )
    return configuration_id


def auto_resolve_configuration_id(profile_id: str) -> str:
    logger.debug("Auto-resolving configuration ID")
    configurations = get_configurations(profile_id)
    if (
        configurations
        and len(configurations) > 0
        and configurations[0].get("item1", {}).get("id")
    ):
        configuration_id = configurations[0]["item1"]["id"]
        logger.debug(f"Auto-resolved configuration ID: {configuration_id}")
        return configuration_id
    else:
        raise Exception(f"No configurations found for profile ID '{profile_id}'.")


def auto_resolve_latest_commit_id(profile_id: str, branch_id: str) -> str:
    logger.debug("Auto-resolving to latest commit")
    commits = get_commits(profile_id, branch_id)
    if commits and len(commits) > 0:
        commit_id = commits[0]["id"]
        logger.debug(f"Auto-resolved to latest commit ID: {commit_id}")
        return commit_id
    else:
        raise Exception(f"No commits found for branch ID '{branch_id}'.")


def resolve_commit_hash_to_id(profile_id: str, branch_id: str, commit_hash: str) -> str:
    logger.debug(f"Resolving commit hash '{commit_hash}' to ID")
    commits = get_commits(profile_id, branch_id)
    found_commit = next((c for c in commits if c.get("hash") == commit_hash), None)
    if not found_commit:
        raise Exception(
            f"Commit with hash '{commit_hash}' not found for branch ID '{branch_id}'."
        )

    commit_id = found_commit["id"]
    logger.debug(f"Resolved commit hash '{commit_hash}' to ID: {commit_id}")
    return commit_id
