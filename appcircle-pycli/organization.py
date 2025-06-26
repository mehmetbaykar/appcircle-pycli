import click
import json
import logging
from .api import (
    get_organizations,
    get_organization_detail,
    get_organization_users,
    invite_user_to_organization,
    re_invite_user_to_organization,
    remove_invitation_from_organization,
    remove_user_from_organization,
    assign_roles_to_user_in_organization,
    create_sub_organization,
    get_user_roles_in_organization,
    add_roles_to_user_in_organization,
    remove_roles_from_user_in_organization,
    clear_user_roles_in_organization,
)

logger = logging.getLogger(__name__)


@click.group()
def organization():
    """
    Commands for managing organizations.
    """
    pass


@organization.command(name="list")
@click.pass_context
def list_organizations(ctx):
    """
    List all organizations.
    """
    if ctx.obj["debug"]:
        logger.info("Listing all organizations.")

    try:
        orgs = get_organizations()
        click.echo(json.dumps(orgs, indent=2))
    except Exception as e:
        if ctx.obj["debug"]:
            logger.error(f"An error occurred: {e}", exc_info=True)
        else:
            click.echo(f"Error: {e}", err=True)


@organization.command(name="view")
@click.argument("organization_id")
@click.pass_context
def view_organization(ctx, organization_id):
    """
    View a specific organization.
    """
    if ctx.obj["debug"]:
        logger.info(f"Viewing organization with ID: {organization_id}")

    try:
        org = get_organization_detail(organization_id)
        click.echo(json.dumps(org, indent=2))
    except Exception as e:
        if ctx.obj["debug"]:
            logger.error(f"An error occurred: {e}", exc_info=True)
        else:
            click.echo(f"Error: {e}", err=True)


@organization.command(name="list-users")
@click.argument("organization_id")
@click.pass_context
def list_users(ctx, organization_id):
    """
    List users in an organization.
    """
    if ctx.obj["debug"]:
        logger.info(f"Listing users for organization with ID: {organization_id}")

    try:
        users = get_organization_users(organization_id)
        click.echo(json.dumps(users, indent=2))
    except Exception as e:
        if ctx.obj["debug"]:
            logger.error(f"An error occurred: {e}", exc_info=True)
        else:
            click.echo(f"Error: {e}", err=True)


@organization.command(name="invite")
@click.argument("organization_id")
@click.argument("email")
@click.option("--role", multiple=True)
@click.pass_context
def invite_user(ctx, organization_id, email, role):
    """
    Invite a user to an organization.
    """
    if ctx.obj["debug"]:
        logger.info(
            f"Inviting user {email} to organization with ID: {organization_id} with roles: {role}"
        )

    try:
        response = invite_user_to_organization(organization_id, email, role)
        click.echo(json.dumps(response, indent=2))
    except Exception as e:
        if ctx.obj["debug"]:
            logger.error(f"An error occurred: {e}", exc_info=True)
        else:
            click.echo(f"Error: {e}", err=True)


@organization.command(name="re-invite")
@click.argument("organization_id")
@click.argument("email")
@click.pass_context
def re_invite_user(ctx, organization_id, email):
    """
    Re-invite a user to an organization.
    """
    if ctx.obj["debug"]:
        logger.info(
            f"Re-inviting user {email} to organization with ID: {organization_id}"
        )

    try:
        response = re_invite_user_to_organization(organization_id, email)
        click.echo(json.dumps(response, indent=2))
    except Exception as e:
        if ctx.obj["debug"]:
            logger.error(f"An error occurred: {e}", exc_info=True)
        else:
            click.echo(f"Error: {e}", err=True)


@organization.command(name="remove-invitation")
@click.argument("organization_id")
@click.argument("email")
@click.pass_context
def remove_invitation(ctx, organization_id, email):
    """
    Remove an invitation from an organization.
    """
    if ctx.obj["debug"]:
        logger.info(
            f"Removing invitation for {email} from organization with ID: {organization_id}"
        )

    try:
        response = remove_invitation_from_organization(organization_id, email)
        click.echo(json.dumps(response, indent=2))
    except Exception as e:
        if ctx.obj["debug"]:
            logger.error(f"An error occurred: {e}", exc_info=True)
        else:
            click.echo(f"Error: {e}", err=True)


@organization.command(name="remove-user")
@click.argument("organization_id")
@click.argument("user_id")
@click.pass_context
def remove_user(ctx, organization_id, user_id):
    """
    Remove a user from an organization.
    """
    if ctx.obj["debug"]:
        logger.info(
            f"Removing user with ID: {user_id} from organization with ID: {organization_id}"
        )

    try:
        response = remove_user_from_organization(organization_id, user_id)
        click.echo(json.dumps(response, indent=2))
    except Exception as e:
        if ctx.obj["debug"]:
            logger.error(f"An error occurred: {e}", exc_info=True)
        else:
            click.echo(f"Error: {e}", err=True)


@organization.command(name="assign-roles")
@click.argument("organization_id")
@click.argument("user_id")
@click.option("--role", multiple=True)
@click.pass_context
def assign_roles(ctx, organization_id, user_id, role):
    """
    Assign roles to a user in an organization.
    """
    if ctx.obj["debug"]:
        logger.info(
            f"Assigning roles {role} to user with ID: {user_id} in organization with ID: {organization_id}"
        )

    try:
        response = assign_roles_to_user_in_organization(organization_id, user_id, role)
        click.echo(json.dumps(response, indent=2))
    except Exception as e:
        if ctx.obj["debug"]:
            logger.error(f"An error occurred: {e}", exc_info=True)
        else:
            click.echo(f"Error: {e}", err=True)


@organization.command(name="create-sub-organization")
@click.argument("name")
@click.pass_context
def create_sub(ctx, name):
    """
    Create a sub-organization.
    """
    if ctx.obj["debug"]:
        logger.info(f"Creating a sub-organization with name: {name}")

    try:
        response = create_sub_organization(name)
        click.echo(json.dumps(response, indent=2))
    except Exception as e:
        if ctx.obj["debug"]:
            logger.error(f"An error occurred: {e}", exc_info=True)
        else:
            click.echo(f"Error: {e}", err=True)


@click.group()
def role():
    """
    Commands for managing user roles in organizations.
    """
    pass


@click.group()
def user():
    """
    Commands for managing users in organizations.
    """
    pass


organization.add_command(role)
organization.add_command(user)


@role.command(name="view")
@click.option(
    "--organizationId", "organization_id", required=True, help="Organization ID"
)
@click.option("--userId", "user_id", required=True, help="User ID")
@click.pass_context
def view_roles(ctx, organization_id, user_id):
    """
    View roles of a user in organization.
    """
    if ctx.obj["debug"]:
        logger.info(
            f"Viewing roles for user with ID: {user_id} in organization with ID: {organization_id}"
        )

    try:
        roles = get_user_roles_in_organization(organization_id, user_id)
        click.echo(json.dumps(roles, indent=2))
    except Exception as e:
        if ctx.obj["debug"]:
            logger.error(f"An error occurred: {e}", exc_info=True)
        else:
            click.echo(f"Error: {e}", err=True)


@role.command(name="add")
@click.option(
    "--organizationId", "organization_id", required=True, help="Organization ID"
)
@click.option("--userId", "user_id", required=True, help="User ID")
@click.option(
    "--role",
    multiple=True,
    required=True,
    help="Roles to add (can be specified multiple times)",
)
@click.pass_context
def add_roles(ctx, organization_id, user_id, role):
    """
    Add roles to a user in organization.
    """
    if ctx.obj["debug"]:
        logger.info(
            f"Adding roles {role} to user with ID: {user_id} in organization with ID: {organization_id}"
        )

    try:
        response = add_roles_to_user_in_organization(
            organization_id, user_id, list(role)
        )
        click.echo(json.dumps(response, indent=2))
    except Exception as e:
        if ctx.obj["debug"]:
            logger.error(f"An error occurred: {e}", exc_info=True)
        else:
            click.echo(f"Error: {e}", err=True)


@role.command(name="remove")
@click.option(
    "--organizationId", "organization_id", required=True, help="Organization ID"
)
@click.option("--userId", "user_id", required=True, help="User ID")
@click.option(
    "--role",
    multiple=True,
    required=True,
    help="Roles to remove (can be specified multiple times)",
)
@click.pass_context
def remove_roles(ctx, organization_id, user_id, role):
    """
    Remove roles from a user in organization.
    """
    if ctx.obj["debug"]:
        logger.info(
            f"Removing roles {role} from user with ID: {user_id} in organization with ID: {organization_id}"
        )

    try:
        response = remove_roles_from_user_in_organization(
            organization_id, user_id, list(role)
        )
        click.echo(json.dumps(response, indent=2))
    except Exception as e:
        if ctx.obj["debug"]:
            logger.error(f"An error occurred: {e}", exc_info=True)
        else:
            click.echo(f"Error: {e}", err=True)


@role.command(name="clear")
@click.option(
    "--organizationId", "organization_id", required=True, help="Organization ID"
)
@click.option("--userId", "user_id", required=True, help="User ID")
@click.pass_context
def clear_roles(ctx, organization_id, user_id):
    """
    Remove all roles from a user in organization.
    """
    if ctx.obj["debug"]:
        logger.info(
            f"Clearing all roles from user with ID: {user_id} in organization with ID: {organization_id}"
        )

    try:
        response = clear_user_roles_in_organization(organization_id, user_id)
        click.echo(json.dumps(response, indent=2))
    except Exception as e:
        if ctx.obj["debug"]:
            logger.error(f"An error occurred: {e}", exc_info=True)
        else:
            click.echo(f"Error: {e}", err=True)


@user.command(name="view")
@click.option(
    "--organizationId", "organization_id", required=True, help="Organization ID"
)
@click.pass_context
def view_users(ctx, organization_id):
    """
    View users of organization.
    """
    if ctx.obj["debug"]:
        logger.info(f"Viewing users for organization with ID: {organization_id}")

    try:
        users = get_organization_users(organization_id)
        click.echo(json.dumps(users, indent=2))
    except Exception as e:
        if ctx.obj["debug"]:
            logger.error(f"An error occurred: {e}", exc_info=True)
        else:
            click.echo(f"Error: {e}", err=True)


@user.command(name="invite")
@click.option(
    "--organizationId", "organization_id", required=True, help="Organization ID"
)
@click.option("--email", required=True, help="User email to invite")
@click.option(
    "--role", multiple=True, help="Roles to assign (can be specified multiple times)"
)
@click.pass_context
def invite_user_cmd(ctx, organization_id, email, role):
    """
    Invite user to organization.
    """
    if ctx.obj["debug"]:
        logger.info(
            f"Inviting user {email} to organization with ID: {organization_id} with roles: {role}"
        )

    try:
        response = invite_user_to_organization(organization_id, email, list(role))
        click.echo(json.dumps(response, indent=2))
    except Exception as e:
        if ctx.obj["debug"]:
            logger.error(f"An error occurred: {e}", exc_info=True)
        else:
            click.echo(f"Error: {e}", err=True)


@user.command(name="re-invite")
@click.option(
    "--organizationId", "organization_id", required=True, help="Organization ID"
)
@click.option("--email", required=True, help="User email to re-invite")
@click.pass_context
def re_invite_user_cmd(ctx, organization_id, email):
    """
    Re-invite user to organization.
    """
    if ctx.obj["debug"]:
        logger.info(
            f"Re-inviting user {email} to organization with ID: {organization_id}"
        )

    try:
        response = re_invite_user_to_organization(organization_id, email)
        click.echo(json.dumps(response, indent=2))
    except Exception as e:
        if ctx.obj["debug"]:
            logger.error(f"An error occurred: {e}", exc_info=True)
        else:
            click.echo(f"Error: {e}", err=True)


@user.command(name="remove")
@click.option(
    "--organizationId", "organization_id", required=True, help="Organization ID"
)
@click.option("--userId", "user_id", required=True, help="User ID to remove")
@click.pass_context
def remove_user_cmd(ctx, organization_id, user_id):
    """
    Remove user from organization.
    """
    if ctx.obj["debug"]:
        logger.info(
            f"Removing user with ID: {user_id} from organization with ID: {organization_id}"
        )

    try:
        response = remove_user_from_organization(organization_id, user_id)
        click.echo(json.dumps(response, indent=2))
    except Exception as e:
        if ctx.obj["debug"]:
            logger.error(f"An error occurred: {e}", exc_info=True)
        else:
            click.echo(f"Error: {e}", err=True)
