# Appcircle CLI (Python)

This is a Python-based command-line interface (CLI) for interacting with the Appcircle API. It allows you to manage various aspects of your Appcircle account, including builds, publishing, distribution, and more.

## Installation

```bash
git clone https://github.com/mehmetbaykar/appcircle-pycli.git
cd appcircle-pycli
pip install -e .

```
or

```bash
pip install git+https://github.com/mehmetbaykar/appcircle-pycli.git
```

## Getting Started

Before you can use the CLI, you need to authenticate with your Appcircle account. You can do this by obtaining a Personal Access Token (PAT) from your Appcircle account and using it to log in:

```bash
appcircle login --pat YOUR_PERSONAL_ACCESS_TOKEN
```

This will save your access token to a configuration file located at `~/.appcircle/config.json`.

## Usage

The CLI is organized into several commands and subcommands. You can get help for any command by using the `--help` flag.

### General Commands

- `appcircle --version`: Show the version of the CLI.
- `appcircle --help`: Show the help message.
- `appcircle --debug`: Run the CLI in debug mode.

### Configuration

The `config` command allows you to manage the CLI's configuration.

- `appcircle config list`: List all configurations.
- `appcircle config get KEY`: Get the value of a configuration property.
- `appcircle config set KEY VALUE`: Set a configuration property.
- `appcircle config current ENV`: Set the current configuration environment.
- `appcircle config add ENV`: Add a new configuration environment.
- `appcircle config reset`: Reset the current configuration to its default values.
- `appcircle config trust`: Trust the SSL certificate of a self-hosted Appcircle server.

### Build

The `build` command allows you to manage your builds.

- `appcircle build start`: Start a new build.
- `appcircle build active-list`: Get a list of active builds.
- `appcircle build list`: Get a list of builds for a specific commit.
- `appcircle build view`: View the details of a specific build.
- `appcircle build download`: Download the artifacts of a specific build.
- `appcircle build download-log`: Download the logs of a specific build.

### Publish

The `publish` command allows you to manage your publish flows.

- `appcircle publish start`: Start a new publish flow.
- `appcircle publish active-list`: Get a list of active publish flows.
- `appcircle publish view`: View the details of a specific publish flow.

### Distribution

The `distribution` command allows you to manage your distribution profiles.

- `appcircle distribution list`: List all distribution profiles.
- `appcircle distribution view`: View the details of a specific distribution profile.
- `appcircle distribution create`: Create a new distribution profile.
- `appcircle distribution update-settings`: Update the settings of a distribution profile.

### Signing Identity

The `signing-identity` command allows you to manage your signing identities.

- `appcircle signing-identity certificate list`: List all certificates.
- `appcircle signing-identity certificate upload`: Upload a new certificate.
- `appcircle signing-identity certificate create`: Create a new certificate signing request.
- `appcircle signing-identity certificate view`: View the details of a specific certificate.
- `appcircle signing-identity certificate download`: Download a specific certificate.
- `appcircle signing-identity certificate remove`: Remove a specific certificate.
- `appcircle signing-identity provisioning-profile list`: List all provisioning profiles.
- `appcircle signing-identity provisioning-profile upload`: Upload a new provisioning profile.
- `appcircle signing-identity provisioning-profile download`: Download a specific provisioning profile.
- `appcircle signing-identity provisioning-profile view`: View the details of a specific provisioning profile.
- `appcircle signing-identity provisioning-profile remove`: Remove a specific provisioning profile.
- `appcircle signing-identity keystore list`: List all keystores.
- `appcircle signing-identity keystore create`: Create a new keystore.
- `appcircle signing-identity keystore upload`: Upload a new keystore.
- `appcircle signing-identity keystore view`: View the details of a specific keystore.
- `appcircle signing-identity keystore download`: Download a specific keystore.
- `appcircle signing-identity keystore remove`: Remove a specific keystore.

### Enterprise App Store

The `enterprise-app-store` command allows you to manage your enterprise app store.

- `appcircle enterprise-app-store list-profiles`: List all enterprise profiles.
- `appcircle enterprise-app-store list-versions`: List all app versions for a specific enterprise profile.
- `appcircle enterprise-app-store publish`: Publish a new app version.
- `appcircle enterprise-app-store unpublish`: Unpublish an app version.
- `appcircle enterprise-app-store remove`: Remove an app version.
- `appcircle enterprise-app-store notify`: Notify users about a new app version.
- `appcircle enterprise-app-store download-link`: Get the download link for an app version.

### Organization

The `organization` command allows you to manage your organizations.

- `appcircle organization list`: List all organizations.
- `appcircle organization view`: View the details of a specific organization.
- `appcircle organization list-users`: List all users in a specific organization.
- `appcircle organization invite`: Invite a new user to an organization.
- `appcircle organization re-invite`: Re-invite a user to an organization.
- `appcircle organization remove-invitation`: Remove a user's invitation to an organization.
- `appcircle organization remove-user`: Remove a user from an organization.
- `appcircle organization assign-roles`: Assign roles to a user in an organization.
- `appcircle organization create-sub-organization`: Create a new sub-organization.
