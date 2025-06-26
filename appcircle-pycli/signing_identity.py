import click
import json
import logging
from .api import (
    get_certificates,
    upload_certificate,
    create_certificate,
    get_certificate_view,
    download_certificate,
    remove_certificate,
    get_provisioning_profiles,
    upload_provisioning_profile,
    download_provisioning_profile,
    get_provisioning_profile_view,
    remove_provisioning_profile,
    get_keystores,
    create_keystore,
    upload_keystore,
    get_keystore_view,
    download_keystore,
    remove_keystore,
)

logger = logging.getLogger(__name__)


@click.group(name="signing-identity")
def signing_identity():
    """Manage iOS certificates, provisioning profiles, and Android keystores for app signing"""
    pass


@click.group()
def certificate():
    """Manage Certificates"""
    pass


@click.group(name="provisioning-profile")
def provisioning_profile():
    """Manage Provisioning Profiles"""
    pass


@click.group()
def keystore():
    """Manage Keystores"""
    pass


signing_identity.add_command(certificate)
signing_identity.add_command(provisioning_profile)
signing_identity.add_command(keystore)


@certificate.command(name="list")
@click.pass_context
def certificate_list(ctx):
    """Certificates List"""
    if ctx.obj["debug"]:
        logger.info("Listing certificates.")

    try:
        certificates = get_certificates()
        click.echo(json.dumps(certificates, indent=2))
    except Exception as e:
        if ctx.obj["debug"]:
            logger.error(f"An error occurred: {e}", exc_info=True)
        else:
            click.echo(f"Error: {e}", err=True)


@certificate.command(name="upload")
@click.option("--path", required=True, help="Certificate Path")
@click.option("--password", required=True, help="Certificate Password")
@click.pass_context
def certificate_upload(ctx, path, password):
    """Upload a New Certificate Bundle (.p12)"""
    if ctx.obj["debug"]:
        logger.info("Uploading a new certificate with the following parameters:")
        logger.info(f"Path: {path}")

    try:
        result = upload_certificate(path, password)
        click.echo(json.dumps(result, indent=2))
    except Exception as e:
        if ctx.obj["debug"]:
            logger.error(f"An error occurred: {e}", exc_info=True)
        else:
            click.echo(f"Error: {e}", err=True)


@certificate.command(name="create")
@click.option("--name", required=True, help="Certificate Name")
@click.option("--email", required=True, help="Email")
@click.option("--country-code", "country_code", required=True, help="Country Code")
@click.pass_context
def certificate_create(ctx, name, email, country_code):
    """Generate Signing Request to Create Certificates"""
    if ctx.obj["debug"]:
        logger.info("Creating a new certificate with the following parameters:")
        logger.info(f"Name: {name}")
        logger.info(f"Email: {email}")
        logger.info(f"Country Code: {country_code}")

    try:
        result = create_certificate(name, email, country_code)
        click.echo(json.dumps(result, indent=2))
    except Exception as e:
        if ctx.obj["debug"]:
            logger.error(f"An error occurred: {e}", exc_info=True)
        else:
            click.echo(f"Error: {e}", err=True)


@certificate.command(name="view")
@click.option(
    "--certificate-bundle-id",
    "certificate_bundle_id",
    required=True,
    help="Certificate Bundle ID",
)
@click.pass_context
def certificate_view(ctx, certificate_bundle_id):
    """View Details of a Certificate Bundle. (.p12)"""
    if ctx.obj["debug"]:
        logger.info(f"Viewing certificate with bundle ID: {certificate_bundle_id}")

    try:
        certificate = get_certificate_view(certificate_bundle_id)
        click.echo(json.dumps(certificate, indent=2))
    except Exception as e:
        if ctx.obj["debug"]:
            logger.error(f"An error occurred: {e}", exc_info=True)
        else:
            click.echo(f"Error: {e}", err=True)


@certificate.command(name="download")
@click.option(
    "--certificate-id", "certificate_id", required=True, help="Certificate ID"
)
@click.option(
    "--path", required=False, help="The Path for certificate to be downloaded"
)
@click.pass_context
def certificate_download(ctx, certificate_id, path):
    """Download Certificate"""
    if ctx.obj["debug"]:
        logger.info("Downloading certificate with the following parameters:")
        logger.info(f"Certificate ID: {certificate_id}")
        logger.info(f"Path: {path}")

    try:
        download_certificate(certificate_id, path)
    except Exception as e:
        if ctx.obj["debug"]:
            logger.error(f"An error occurred: {e}", exc_info=True)
        else:
            click.echo(f"Error: {e}", err=True)


@certificate.command(name="remove")
@click.option(
    "--certificate-id", "certificate_id", required=True, help="Certificate ID"
)
@click.pass_context
def certificate_remove(ctx, certificate_id):
    """Remove Certificate"""
    if ctx.obj["debug"]:
        logger.info(f"Removing certificate with ID: {certificate_id}")

    try:
        result = remove_certificate(certificate_id)
        click.echo(json.dumps(result, indent=2))
    except Exception as e:
        if ctx.obj["debug"]:
            logger.error(f"An error occurred: {e}", exc_info=True)
        else:
            click.echo(f"Error: {e}", err=True)


@provisioning_profile.command(name="list")
@click.pass_context
def provisioning_profile_list(ctx):
    """Provisioning Profile List"""
    if ctx.obj["debug"]:
        logger.info("Listing provisioning profiles.")

    try:
        profiles = get_provisioning_profiles()
        click.echo(json.dumps(profiles, indent=2))
    except Exception as e:
        if ctx.obj["debug"]:
            logger.error(f"An error occurred: {e}", exc_info=True)
        else:
            click.echo(f"Error: {e}", err=True)


@provisioning_profile.command(name="upload")
@click.option("--path", required=True, help="Provisioning Profile Path")
@click.pass_context
def provisioning_profile_upload(ctx, path):
    """Upload a Provisioning Profile (.mobileprovision)"""
    if ctx.obj["debug"]:
        logger.info(f"Uploading provisioning profile from path: {path}")

    try:
        result = upload_provisioning_profile(path)
        click.echo(json.dumps(result, indent=2))
    except Exception as e:
        if ctx.obj["debug"]:
            logger.error(f"An error occurred: {e}", exc_info=True)
        else:
            click.echo(f"Error: {e}", err=True)


@provisioning_profile.command(name="download")
@click.option(
    "--provisioning-profile-id",
    "provisioning_profile_id",
    required=True,
    help="Provisioning Profile ID",
)
@click.option(
    "--path", required=False, help="The Path for provisioning profile to be downloaded"
)
@click.pass_context
def provisioning_profile_download(ctx, provisioning_profile_id, path):
    """Download Provisioning Profile"""
    if ctx.obj["debug"]:
        logger.info("Downloading provisioning profile with the following parameters:")
        logger.info(f"Provisioning Profile ID: {provisioning_profile_id}")
        logger.info(f"Path: {path}")

    try:
        download_provisioning_profile(provisioning_profile_id, path)
    except Exception as e:
        if ctx.obj["debug"]:
            logger.error(f"An error occurred: {e}", exc_info=True)
        else:
            click.echo(f"Error: {e}", err=True)


@provisioning_profile.command(name="view")
@click.option(
    "--provisioning-profile-id",
    "provisioning_profile_id",
    required=True,
    help="Provisioning Profile ID",
)
@click.pass_context
def provisioning_profile_view(ctx, provisioning_profile_id):
    """View Details of a Provisioning Profile"""
    if ctx.obj["debug"]:
        logger.info(f"Viewing provisioning profile with ID: {provisioning_profile_id}")

    try:
        profile = get_provisioning_profile_view(provisioning_profile_id)
        click.echo(json.dumps(profile, indent=2))
    except Exception as e:
        if ctx.obj["debug"]:
            logger.error(f"An error occurred: {e}", exc_info=True)
        else:
            click.echo(f"Error: {e}", err=True)


@provisioning_profile.command(name="remove")
@click.option(
    "--provisioning-profile-id",
    "provisioning_profile_id",
    required=True,
    help="Provisioning Profile ID",
)
@click.pass_context
def provisioning_profile_remove(ctx, provisioning_profile_id):
    """Remove Provisioning Profile"""
    if ctx.obj["debug"]:
        logger.info(f"Removing provisioning profile with ID: {provisioning_profile_id}")

    try:
        result = remove_provisioning_profile(provisioning_profile_id)
        click.echo(json.dumps(result, indent=2))
    except Exception as e:
        if ctx.obj["debug"]:
            logger.error(f"An error occurred: {e}", exc_info=True)
        else:
            click.echo(f"Error: {e}", err=True)


@keystore.command(name="list")
@click.pass_context
def keystore_list(ctx):
    """Keystores List"""
    if ctx.obj["debug"]:
        logger.info("Listing keystores.")

    try:
        keystores = get_keystores()
        click.echo(json.dumps(keystores, indent=2))
    except Exception as e:
        if ctx.obj["debug"]:
            logger.error(f"An error occurred: {e}", exc_info=True)
        else:
            click.echo(f"Error: {e}", err=True)


@keystore.command(name="create")
@click.option("--name", required=True, help="Keystore Name")
@click.option("--password", required=True, help="Keystore Password")
@click.option("--alias", required=True, help="Alias")
@click.option(
    "--alias-password", "alias_password", required=True, help="Alias password"
)
@click.option("--validity", required=True, help="Validity (Years)")
@click.pass_context
def keystore_create(ctx, name, password, alias, alias_password, validity):
    """Generate a New Keystore"""
    if ctx.obj["debug"]:
        logger.info("Creating a new keystore with the following parameters:")
        logger.info(f"Name: {name}")
        logger.info(f"Alias: {alias}")
        logger.info(f"Validity: {validity}")

    try:
        result = create_keystore(name, password, alias, alias_password, validity)
        click.echo(json.dumps(result, indent=2))
    except Exception as e:
        if ctx.obj["debug"]:
            logger.error(f"An error occurred: {e}", exc_info=True)
        else:
            click.echo(f"Error: {e}", err=True)


@keystore.command(name="upload")
@click.option("--path", required=True, help="Keystore Path")
@click.option("--password", required=True, help="Keystore Password")
@click.option(
    "--alias-password", "alias_password", required=True, help="Alias password"
)
@click.pass_context
def keystore_upload(ctx, path, password, alias_password):
    """Upload Keystore File (.jks or .keystore)"""
    if ctx.obj["debug"]:
        logger.info("Uploading a new keystore with the following parameters:")
        logger.info(f"Path: {path}")

    try:
        result = upload_keystore(path, password, alias_password)
        click.echo(json.dumps(result, indent=2))
    except Exception as e:
        if ctx.obj["debug"]:
            logger.error(f"An error occurred: {e}", exc_info=True)
        else:
            click.echo(f"Error: {e}", err=True)


@keystore.command(name="view")
@click.option("--keystore-id", "keystore_id", required=True, help="Keystore ID")
@click.pass_context
def keystore_view(ctx, keystore_id):
    """View Details of a Keystore"""
    if ctx.obj["debug"]:
        logger.info(f"Viewing keystore with ID: {keystore_id}")

    try:
        keystore = get_keystore_view(keystore_id)
        click.echo(json.dumps(keystore, indent=2))
    except Exception as e:
        if ctx.obj["debug"]:
            logger.error(f"An error occurred: {e}", exc_info=True)
        else:
            click.echo(f"Error: {e}", err=True)


@keystore.command(name="download")
@click.option("--keystore-id", "keystore_id", required=True, help="Keystore ID")
@click.option("--path", required=False, help="The Path for keystore to be downloaded")
@click.pass_context
def keystore_download(ctx, keystore_id, path):
    """Download Keystore"""
    if ctx.obj["debug"]:
        logger.info("Downloading keystore with the following parameters:")
        logger.info(f"Keystore ID: {keystore_id}")
        logger.info(f"Path: {path}")

    try:
        download_keystore(keystore_id, path)
    except Exception as e:
        if ctx.obj["debug"]:
            logger.error(f"An error occurred: {e}", exc_info=True)
        else:
            click.echo(f"Error: {e}", err=True)


@keystore.command(name="remove")
@click.option("--keystore-id", "keystore_id", required=True, help="Keystore ID")
@click.pass_context
def keystore_remove(ctx, keystore_id):
    """Remove Keystore"""
    if ctx.obj["debug"]:
        logger.info(f"Removing keystore with ID: {keystore_id}")

    try:
        result = remove_keystore(keystore_id)
        click.echo(json.dumps(result, indent=2))
    except Exception as e:
        if ctx.obj["debug"]:
            logger.error(f"An error occurred: {e}", exc_info=True)
        else:
            click.echo(f"Error: {e}", err=True)
