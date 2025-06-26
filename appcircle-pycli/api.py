import requests
import click
import json
import logging
import urllib.parse
from typing import Optional, Dict, Any
from .config_manager import ConfigManager

logger = logging.getLogger(__name__)


class APIError(Exception):
    """Base exception for API-related errors"""
    def __init__(self, status_code: int, message: str, response_data: Optional[Dict] = None):
        self.status_code = status_code
        self.message = message
        self.response_data = response_data
        super().__init__(f"API Error {status_code}: {message}")


class AuthenticationError(APIError):
    """Authentication-related errors"""
    pass


class RateLimitError(APIError):
    """Rate limiting errors"""
    pass


class ValidationError(APIError):
    """Request validation errors"""
    pass


class API:
    def __init__(self):
        config_manager = ConfigManager()
        config = config_manager.get_config()
        current_env = config["current"]
        self.api_hostname = config["envs"][current_env]["API_HOSTNAME"]
        self._access_token = config["envs"][current_env]["AC_ACCESS_TOKEN"]
        self.headers = {
            "Authorization": f"Bearer {self._access_token}",
            "Content-Type": "application/json",
        }
        
        if not self._access_token or self._access_token.strip() == "":
            raise AuthenticationError(401, "Access token is required but not configured")
    
    def _get_auth_headers(self):
        """Get authentication headers securely"""
        if not self._access_token:
            raise AuthenticationError(401, "No access token available")
        
        return {
            "Authorization": f"Bearer {self._access_token}",
            "Content-Type": "application/json",
        }
    
    def _get_safe_headers_for_logging(self):
        """Get headers with sensitive data redacted for logging"""
        return {k: v if k != "Authorization" else "Bearer [REDACTED]" 
                for k, v in self.headers.items()}
    
    def _validate_token(self):
        """Validate token format and potentially check expiry"""
        if not self._access_token:
            return False
        return True
    
    def _handle_response(self, response: requests.Response) -> Any:
        """Process response with proper error handling"""
        logger.debug(f"Response: {response.status_code} {response.reason}")
        
        if response.status_code == 401:
            try:
                error_data = response.json() if response.content else {}
                message = error_data.get('message', 'Authentication failed')
                raise AuthenticationError(401, message, error_data)
            except json.JSONDecodeError:
                raise AuthenticationError(401, "Authentication failed")
        elif response.status_code == 403:
            try:
                error_data = response.json() if response.content else {}
                message = error_data.get('message', 'Access forbidden')
                raise APIError(403, message, error_data)
            except json.JSONDecodeError:
                raise APIError(403, "Access forbidden")
        elif response.status_code == 429:
            try:
                error_data = response.json() if response.content else {}
                message = error_data.get('message', 'Rate limit exceeded')
                raise RateLimitError(429, message, error_data)
            except json.JSONDecodeError:
                raise RateLimitError(429, "Rate limit exceeded")
        elif response.status_code >= 400:
            try:
                error_data = response.json() if response.content else {}
                message = error_data.get('message', f"HTTP {response.status_code}")
                raise APIError(response.status_code, message, error_data)
            except json.JSONDecodeError:
                raise APIError(response.status_code, response.text or f"HTTP {response.status_code}")
        
        if response.status_code == 204 or not response.content:
            return {}
        
        try:
            return response.json()
        except json.JSONDecodeError:
            return response.text

    def get(self, path, params=None):
        url = f"{self.api_hostname}{path}"
        logger.debug(f"GET {url}")
        safe_headers = self._get_safe_headers_for_logging()
        logger.debug(f"Headers: {safe_headers}")
        logger.debug(f"Params: {params}")

        response = requests.get(url, headers=self._get_auth_headers(), params=params, timeout=30)

        logger.debug(f"Response Status: {response.status_code} {response.reason}")
        logger.debug(f"Response Headers: {dict(response.headers)}")
        if response.status_code < 400 and len(response.text) < 1000:
            logger.debug(f"Response Text: {response.text[:500]}..." if len(response.text) > 500 else f"Response Text: {response.text}")
        else:
            logger.debug(f"Response length: {len(response.text)} bytes")

        return self._handle_response(response)

    def post(self, path, data=None, files=None, content_type=None):
        url = f"{self.api_hostname}{path}"
        headers = self._get_auth_headers().copy()

        if content_type:
            headers["Content-Type"] = content_type
        elif files:
            if "Content-Type" in headers:
                del headers["Content-Type"]

        logger.debug(f"POST {url}")
        safe_headers = {k: v if k != "Authorization" else "Bearer [REDACTED]" 
                      for k, v in headers.items()}
        logger.debug(f"Headers: {safe_headers}")
        logger.debug(f"Data: {data}")
        logger.debug(f"Files: {files}")

        response = requests.post(
            url,
            headers=headers,
            json=data if not files else None,
            data=data if files else None,
            files=files,
            timeout=30,
        )

        logger.debug(f"Response Status: {response.status_code}")
        logger.debug(f"Response Headers: {dict(response.headers)}")
        logger.debug(f"Response Text: {response.text}")

        return self._handle_response(response)

    def put(self, path, data=None):
        url = f"{self.api_hostname}{path}"
        logger.debug(f"PUT {url}")
        safe_headers = self._get_safe_headers_for_logging()
        logger.debug(f"Headers: {safe_headers}")
        
        response = requests.put(url, headers=self._get_auth_headers(), json=data, timeout=30)
        
        return self._handle_response(response)

    def patch(self, path, data=None):
        url = f"{self.api_hostname}{path}"
        logger.debug(f"PATCH {url}")
        safe_headers = self._get_safe_headers_for_logging()
        logger.debug(f"Headers: {safe_headers}")
        
        response = requests.patch(url, headers=self._get_auth_headers(), json=data, timeout=30)
        
        return self._handle_response(response)

    def delete(self, path, data=None):
        url = f"{self.api_hostname}{path}"
        logger.debug(f"DELETE {url}")
        safe_headers = self._get_safe_headers_for_logging()
        logger.debug(f"Headers: {safe_headers}")
        
        response = requests.delete(url, headers=self._get_auth_headers(), json=data, timeout=30)
        
        return self._handle_response(response)

    def download(self, path):
        url = f"{self.api_hostname}{path}"
        logger.debug(f"DOWNLOAD {url}")
        safe_headers = self._get_safe_headers_for_logging()
        logger.debug(f"Headers: {safe_headers}")
        
        response = requests.get(url, headers=self._get_auth_headers(), stream=True, timeout=30)
        
        logger.debug(f"Response Status: {response.status_code} {response.reason}")
        if response.status_code >= 400:
            self._handle_response(response)
        return response


def get_api():
    return API()


def get_distribution_profiles():
    return get_api().get("/distribution/v2/profiles")


def get_distribution_profile_by_id(dist_profile_id):
    return get_api().get(f"/distribution/v2/profiles/{dist_profile_id}")


def update_distribution_profile_settings(dist_profile_id, testing_group_ids):
    return get_api().patch(
        f"/distribution/v2/profiles/{dist_profile_id}",
        {"testingGroupIds": testing_group_ids},
    )


def create_distribution_profile(name):
    return get_api().post("/distribution/v1/profiles", {"name": name})


def get_testing_groups():
    return get_api().get("/distribution/v2/testing-groups")


def get_testing_group_by_id(testing_group_id):
    return get_api().get(f"/distribution/v2/testing-groups/{testing_group_id}")


def create_testing_group(name):
    return get_api().post("/distribution/v2/testing-groups", {"name": name})


def delete_testing_group(testing_group_id):
    return get_api().delete(f"/distribution/v2/testing-groups/{testing_group_id}")


def add_tester_to_testing_group(testing_group_id, tester_email):
    return get_api().post(
        f"/distribution/v2/testing-groups/{testing_group_id}/testers", [tester_email]
    )


def remove_tester_from_testing_group(testing_group_id, tester_email):
    return get_api().delete(
        f"/distribution/v2/testing-groups/{testing_group_id}/testers",
        data=[tester_email],
    )


def get_testing_distribution_upload_information(dist_profile_id, file_size, file_name):
    return get_api().get(
        f"/distribution/v1/profiles/{dist_profile_id}/app-versions?action=uploadInformation&fileSize={file_size}&fileName={file_name}"
    )


def commit_testing_distribution_file_upload(dist_profile_id, file_id, file_name):
    return get_api().post(
        f"/distribution/v1/profiles/{dist_profile_id}/app-versions?action=commitFileUpload",
        {"fileId": file_id, "fileName": file_name},
    )


def update_testing_distribution_release_notes(dist_profile_id, version_id, message):
    return get_api().patch(
        f"/distribution/v1/profiles/{dist_profile_id}/app-versions/{version_id}?action=updateMessage",
        {"message": message},
    )


def get_enterprise_profiles():
    return get_api().get("/store/v2/profiles")


def get_enterprise_app_versions(ent_profile_id, publish_type):
    version_type = ""
    if publish_type == "1":
        version_type = "?publishtype=Beta"
    elif publish_type == "2":
        version_type = "?publishtype=Live"
    return get_api().get(
        f"/store/v2/profiles/{ent_profile_id}/app-versions{version_type}"
    )


def publish_enterprise_app_version(
    ent_profile_id, ent_version_id, summary, release_notes, publish_type
):
    return get_api().patch(
        f"/store/v2/profiles/{ent_profile_id}/app-versions/{ent_version_id}?action=publish",
        {
            "summary": summary,
            "releaseNotes": release_notes,
            "publishType": publish_type,
        },
    )


def unpublish_enterprise_app_version(ent_profile_id, ent_version_id):
    return get_api().patch(
        f"/store/v2/profiles/{ent_profile_id}/app-versions/{ent_version_id}?action=unpublish",
        {},
    )


def remove_enterprise_app_version(ent_profile_id, ent_version_id):
    return get_api().delete(
        f"/store/v2/profiles/{ent_profile_id}/app-versions/{ent_version_id}"
    )


def notify_enterprise_app_version(ent_profile_id, ent_version_id, subject, message):
    return get_api().post(
        f"/store/v2/profiles/{ent_profile_id}/app-versions/{ent_version_id}?action=notify",
        {"subject": subject, "message": message},
    )


def get_enterprise_download_link(ent_profile_id, ent_version_id):
    return get_api().get(
        f"/store/v2/profiles/{ent_profile_id}/app-versions/{ent_version_id}?action=download"
    )


def get_organizations():
    return get_api().get("/identity/v1/organizations")


def get_organization_detail(organization_id):
    return get_api().get(f"/identity/v1/organizations/{organization_id}")


def get_organization_users(organization_id):
    return get_api().get(f"/identity/v1/organizations/{organization_id}/users")


def invite_user_to_organization(organization_id, email, role):
    return get_api().patch(
        f"/identity/v1/users?action=invite&organizationId={organization_id}",
        {
            "userEmail": email,
            "organizationsAndRoles": [
                {"organizationId": organization_id, "roles": role}
            ],
        },
    )


def re_invite_user_to_organization(organization_id, email):
    return get_api().patch(
        f"/identity/v1/organizations/{organization_id}/invitations?action=re-invite",
        {"userEmail": email},
    )


def remove_invitation_from_organization(organization_id, email):
    return get_api().delete(
        f"/identity/v1/organizations/{organization_id}/invitations",
        data={"userEmail": email},
    )


def remove_user_from_organization(organization_id, user_id):
    return get_api().delete(
        f"/identity/v1/organizations/{organization_id}?action=remove&userId={user_id}"
    )


def assign_roles_to_user_in_organization(organization_id, user_id, role):
    return get_api().put(
        f"/identity/v1/organizations/{organization_id}/users/{user_id}/roles",
        {"roles": role},
    )


def create_sub_organization(name):
    return get_api().post(
        "/identity/v1/organizations/current/sub-organizations", {"name": name}
    )


def get_publish_profiles(platform):
    return get_api().get(f"/publish/v2/profiles/{platform}")


def create_publish_profile(platform, name):
    return get_api().post(f"/publish/v2/profiles/{platform}", {"name": name})


def delete_publish_profile(platform, profile_id):
    return get_api().delete(f"/publish/v2/profiles/{platform}/{profile_id}")


def rename_publish_profile(platform, profile_id, new_name):
    return get_api().patch(
        f"/publish/v2/profiles/{platform}/{profile_id}", {"name": new_name}
    )


def get_publish_profile_settings(platform, profile_id):
    return get_api().get(f"/publish/v2/profiles/{platform}/{profile_id}")


def update_publish_profile_settings(platform, profile_id, settings):
    return get_api().patch(
        f"/publish/v2/profiles/{platform}/{profile_id}", {"profileSettings": settings}
    )


def get_publish_profile_versions(platform, profile_id):
    return get_api().get(f"/publish/v2/profiles/{platform}/{profile_id}/app-versions")


def delete_publish_profile_version(platform, profile_id, version_id):
    return get_api().delete(
        f"/publish/v2/profiles/{platform}/{profile_id}/app-versions/{version_id}"
    )


def download_publish_profile_version(platform, profile_id, version_id, path):
    response = get_api().download(
        f"/publish/v2/profiles/{platform}/{profile_id}/app-versions/{version_id}?action=download"
    )
    file_path = path if path else f"{version_id}.zip"
    with open(file_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    click.echo(f"Version downloaded to {file_path}")


def mark_as_rc(platform, profile_id, version_id):
    return get_api().patch(
        f"/publish/v2/profiles/{platform}/{profile_id}/app-versions/{version_id}?action=releaseCandidate",
        {"ReleaseCandidate": True},
    )


def unmark_as_rc(platform, profile_id, version_id):
    return get_api().patch(
        f"/publish/v2/profiles/{platform}/{profile_id}/app-versions/{version_id}?action=releaseCandidate",
        {"ReleaseCandidate": False},
    )


def update_release_note(platform, profile_id, version_id, note):
    return get_api().patch(
        f"/publish/v2/profiles/{platform}/{profile_id}/app-versions/{version_id}?action=releaseNotes",
        {"summary": note},
    )


def get_active_publishes():
    publishes = get_api().get("/build/v1/queue/my-dashboard?page=1&size=1000")
    if "data" in publishes and publishes["data"] is not None:
        return [p for p in publishes["data"] if p.get("publishId") is not None]
    return []


def start_existing_publish_flow(profile_id, platform, publish_id):
    return get_api().post(
        f"publish/v2/profiles/{platform}/{profile_id}/publish/{publish_id}?action=restart",
        data={},
    )


def get_publish_variable_groups():
    return get_api().get("publish/v2/variable-groups")


def get_publish_variable_list_by_group_id(group_id):
    return get_api().get(f"publish/v2/variable-groups/{group_id}")


def upload_publish_environment_variables_from_file(group_id, file_path):
    with open(file_path, "rb") as f:
        files = {"envVariablesFile": f}
        data = {"variableGroupId": group_id}
        return get_api().post(
            f"/publish/v1/variable-groups/{group_id}/upload-variables-file",
            data=data,
            files=files,
        )


def get_app_version_detail(profile_id, platform, app_version_id):
    return get_api().get(
        f"publish/v1/profiles/{platform}/{profile_id}/app-versions/{app_version_id}"
    )


def upload_app_version(app, profile_id, platform):
    with open(app, "rb") as f:
        files = {"File": f}
        return get_api().post(
            f"/publish/v2/profiles/{platform}/{profile_id}/app-versions", files=files
        )


def get_build_profiles():
    return get_api().get("/build/v2/profiles")


def get_branches(profile_id):
    return get_api().get(f"/build/v2/profiles/{profile_id}")


def get_commits(profile_id, branch_id):
    return get_api().get(f"/build/v2/commits?profileId={profile_id}&branchId={branch_id}")


def get_workflows(profile_id):
    return get_api().get(f"/build/v2/profiles/{profile_id}/workflows")


def get_configurations(profile_id):
    return get_api().get(f"/build/v2/profiles/{profile_id}/configurations")


def start_build(options):
    """
    Start a build with proper name-to-ID resolution and correct API endpoint
    Matches TypeScript implementation exactly
    """
    api = get_api()

    query_params = {
        "action": "build",
        "workflowId": options["workflowId"],
        "configurationId": options["configurationId"],
    }
    query_string = urllib.parse.urlencode(query_params)
    endpoint = f"/build/v2/commits/{options['commitId']}?{query_string}"

    logger.debug(f"Final endpoint: {endpoint}")
    logger.debug(
        f"Final parameters - commitId: {options['commitId']}, workflowId: {options['workflowId']}, configurationId: {options['configurationId']}"
    )

    return api.post(
        endpoint, data="{}", content_type="application/x-www-form-urlencoded"
    )


def get_active_builds():
    """Get active builds using the correct API endpoint"""
    builds = get_api().get("/build/v1/queue/my-dashboard?page=1&size=1000")
    if "data" in builds and builds["data"] is not None:
        return [b for b in builds["data"] if b.get("buildId") is not None]
    return []


def get_builds(profile_id, branch_id, commit_id):
    return get_api().get(
        f"/build/v2/profiles/{profile_id}/branches/{branch_id}/commits/{commit_id}/builds"
    )


def get_build(profile_id, branch_id, commit_id, build_id):
    return get_api().get(
        f"/build/v2/profiles/{profile_id}/branches/{branch_id}/commits/{commit_id}/builds/{build_id}"
    )


def get_task_status(task_id):
    return get_api().get(f"/task/v1/tasks/{task_id}")


def get_build_status_from_queue(task_id):
    return get_api().get(f"/build/v1/queue/{task_id}")


def get_latest_build_id(branch_id, profile_id):
    response = get_api().get(
        f"/build/v1/builds?branchId={branch_id}&profileId={profile_id}"
    )
    if response and len(response) > 0:
        sorted_builds = sorted(response, key=lambda x: x["startDate"], reverse=True)
        return sorted_builds[0].get("id")
    return None


def download_task_log(task_id, path):
    response = get_api().download(f"/build/v1/queue/logs/{task_id}")
    file_path = path if path else f"build-task-{task_id}-log.txt"
    with open(file_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    click.echo(f"Log downloaded to {file_path}")


def download_artifacts(profile_id, branch_id, commit_id, build_id, path):
    response = get_api().download(
        f"/build/v2/profiles/{profile_id}/branches/{branch_id}/commits/{commit_id}/builds/{build_id}/download"
    )
    file_path = path if path else f"{build_id}_artifacts.zip"
    with open(file_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    click.echo(f"Artifacts downloaded to {file_path}")


def download_log(profile_id, branch_id, commit_id, build_id, path):
    response = get_api().download(
        f"/build/v2/profiles/{profile_id}/branches/{branch_id}/commits/{commit_id}/builds/{build_id}/log"
    )
    file_path = path if path else f"{build_id}.log"
    with open(file_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    click.echo(f"Log downloaded to {file_path}")


def get_variable_groups():
    return get_api().get("/build/v2/variable-groups")


def create_variable_group(name):
    return get_api().post("/build/v2/variable-groups", {"name": name})


def upload_build_variables_from_file(variable_group_id, file_path):
    with open(file_path, "rb") as f:
        files = {"envVariablesFile": f}
        data = {"variableGroupId": variable_group_id}
        return get_api().post(
            f"/build/v1/variable-groups/{variable_group_id}/upload-variables-file",
            data=data,
            files=files,
        )


def download_variables(variable_group_id, path):
    variables = get_api().get(
        f"/build/v2/variable-groups/{variable_group_id}/variables"
    )
    file_path = path if path else f"{variable_group_id}.json"
    with open(file_path, "w") as f:
        json.dump(variables, f, indent=2)
    click.echo(f"Variables downloaded to {file_path}")


def create_variable(variable_group_id, data):
    return get_api().post(
        f"/build/v2/variable-groups/{variable_group_id}/variables", data
    )


def get_variables(variable_group_id):
    return get_api().get(f"/build/v2/variable-groups/{variable_group_id}/variables")


def get_certificates():
    return get_api().get("/signing-identity/v2/certificates")


def upload_certificate(path, password):
    with open(path, "rb") as f:
        files = {"file": f}
        data = {"password": password}
        return get_api().post(
            "/signing-identity/v2/certificates", files=files, data=data
        )


def create_certificate(name, email, country_code):
    data = {"name": name, "email": email, "countryCode": country_code}
    return get_api().post("/signing-identity/v2/certificates/csr", data=data)


def get_certificate_view(certificate_bundle_id):
    return get_api().get(f"/signing-identity/v2/certificates/{certificate_bundle_id}")


def download_certificate(certificate_id, path):
    response = get_api().download(
        f"/signing-identity/v2/certificates/{certificate_id}/download"
    )
    file_path = path if path else f"{certificate_id}.p12"
    with open(file_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    click.echo(f"Certificate downloaded to {file_path}")


def remove_certificate(certificate_id):
    return get_api().delete(f"/signing-identity/v2/certificates/{certificate_id}")


def get_provisioning_profiles():
    return get_api().get("/signing-identity/v2/provisioning-profiles")


def upload_provisioning_profile(path):
    with open(path, "rb") as f:
        files = {"file": f}
        return get_api().post("/signing-identity/v2/provisioning-profiles", files=files)


def download_provisioning_profile(provisioning_profile_id, path):
    response = get_api().download(
        f"/signing-identity/v2/provisioning-profiles/{provisioning_profile_id}/download"
    )
    file_path = path if path else f"{provisioning_profile_id}.mobileprovision"
    with open(file_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    click.echo(f"Provisioning profile downloaded to {file_path}")


def get_provisioning_profile_view(provisioning_profile_id):
    return get_api().get(
        f"/signing-identity/v2/provisioning-profiles/{provisioning_profile_id}"
    )


def remove_provisioning_profile(provisioning_profile_id):
    return get_api().delete(
        f"/signing-identity/v2/provisioning-profiles/{provisioning_profile_id}"
    )


def get_keystores():
    return get_api().get("/signing-identity/v2/keystores")


def create_keystore(name, password, alias, alias_password, validity):
    data = {
        "name": name,
        "password": password,
        "alias": alias,
        "aliasPassword": alias_password,
        "validity": validity,
    }
    return get_api().post("/signing-identity/v2/keystores", data=data)


def upload_keystore(path, password, alias_password):
    with open(path, "rb") as f:
        files = {"file": f}
        data = {"password": password, "aliasPassword": alias_password}
        return get_api().post(
            "/signing-identity/v2/keystores/upload", files=files, data=data
        )


def get_keystore_view(keystore_id):
    return get_api().get(f"/signing-identity/v2/keystores/{keystore_id}")


def download_keystore(keystore_id, path):
    response = get_api().download(
        f"/signing-identity/v2/keystores/{keystore_id}/download"
    )
    file_path = path if path else f"{keystore_id}.jks"
    with open(file_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    click.echo(f"Keystore downloaded to {file_path}")


def remove_keystore(keystore_id):
    return get_api().delete(f"/signing-identity/v2/keystores/{keystore_id}")


def upload_testing_distribution(dist_profile_id, app_path, message=None):
    """Upload mobile app to testing distribution profile"""
    with open(app_path, "rb") as f:
        files = {"File": f}
        data = {}
        if message:
            data["message"] = message
        return get_api().post(
            f"/distribution/v1/profiles/{dist_profile_id}/app-versions",
            files=files,
            data=data,
        )


def get_testing_distribution_profile_settings(dist_profile_id):
    """Get testing distribution profile settings"""
    return get_api().get(f"/distribution/v2/profiles/{dist_profile_id}/settings")


def update_testing_distribution_auto_send_settings(
    dist_profile_id, testing_group_ids, auto_send_enabled
):
    """Update auto-send settings for testing distribution profile"""
    data = {"testingGroupIds": testing_group_ids, "autoSendEnabled": auto_send_enabled}
    return get_api().patch(
        f"/distribution/v2/profiles/{dist_profile_id}/settings", data
    )


def get_user_roles_in_organization(organization_id, user_id):
    """Get roles of a user in organization"""
    return get_api().get(
        f"/identity/v1/organizations/{organization_id}/users/{user_id}/roles"
    )


def add_roles_to_user_in_organization(organization_id, user_id, roles):
    """Add roles to a user in organization"""
    return get_api().post(
        f"/identity/v1/organizations/{organization_id}/users/{user_id}/roles",
        {"roles": roles},
    )


def remove_roles_from_user_in_organization(organization_id, user_id, roles):
    """Remove specific roles from a user in organization"""
    return get_api().delete(
        f"/identity/v1/organizations/{organization_id}/users/{user_id}/roles",
        data={"roles": roles},
    )


def clear_user_roles_in_organization(organization_id, user_id):
    """Remove all roles from a user in organization"""
    return get_api().delete(
        f"/identity/v1/organizations/{organization_id}/users/{user_id}/roles"
    )


def upload_enterprise_app_for_profile(ent_profile_id, app_path, name, summary):
    """Upload app version for enterprise profile"""
    with open(app_path, "rb") as f:
        files = {"File": f}
        data = {"name": name, "summary": summary}
        return get_api().post(
            f"/store/v2/profiles/{ent_profile_id}/app-versions", files=files, data=data
        )


def upload_enterprise_app_without_profile(app_path, name, summary):
    """Upload app version without specific enterprise profile"""
    with open(app_path, "rb") as f:
        files = {"File": f}
        data = {"name": name, "summary": summary}
        return get_api().post("/store/v2/app-versions", files=files, data=data)


def create_publish_variable_group(name):
    """Create a new publish variable group"""
    return get_api().post("/publish/v2/variable-groups", {"name": name})


def delete_publish_variable_group(group_id):
    """Delete a publish variable group"""
    return get_api().delete(f"/publish/v2/variable-groups/{group_id}")


def download_publish_variables(group_id, path):
    """Download publish variables as JSON"""
    variables = get_api().get(f"/publish/v2/variable-groups/{group_id}")
    file_path = path if path else f"publish_variables_{group_id}.json"
    with open(file_path, "w") as f:
        json.dump(variables, f, indent=2)
    click.echo(f"Publish variables downloaded to {file_path}")


def get_variable_group_details(variable_group_id):
    """Get details of a specific variable group"""
    return get_api().get(f"/build/v2/variable-groups/{variable_group_id}")


def add_tester_to_distribution_profile(dist_profile_id, tester_email):
    """Add tester directly to distribution profile"""
    return get_api().post(
        f"/distribution/v2/profiles/{dist_profile_id}/testers", {"email": tester_email}
    )


def remove_tester_from_distribution_profile(dist_profile_id, tester_email):
    """Remove tester from distribution profile"""
    return get_api().delete(
        f"/distribution/v2/profiles/{dist_profile_id}/testers",
        data={"email": tester_email},
    )


def add_testing_group_to_distribution_profile(dist_profile_id, testing_group_id):
    """Add testing group to distribution profile"""
    return get_api().post(
        f"/distribution/v2/profiles/{dist_profile_id}/testing-groups",
        {"testingGroupId": testing_group_id},
    )


def remove_testing_group_from_distribution_profile(dist_profile_id, testing_group_id):
    """Remove testing group from distribution profile"""
    return get_api().delete(
        f"/distribution/v2/profiles/{dist_profile_id}/testing-groups",
        data={"testingGroupId": testing_group_id},
    )


def add_workflow_to_distribution_profile(dist_profile_id, workflow_id):
    """Add workflow to distribution profile"""
    return get_api().post(
        f"/distribution/v2/profiles/{dist_profile_id}/workflows",
        {"workflowId": workflow_id},
    )


def remove_workflow_from_distribution_profile(dist_profile_id, workflow_id):
    """Remove workflow from distribution profile"""
    return get_api().delete(
        f"/distribution/v2/profiles/{dist_profile_id}/workflows",
        data={"workflowId": workflow_id},
    )


def create_build_configuration(profile_id, configuration_data):
    """Create new build configuration"""
    return get_api().post(
        f"/build/v2/profiles/{profile_id}/configurations", configuration_data
    )


def update_build_configuration(profile_id, configuration_id, configuration_data):
    """Update build configuration"""
    return get_api().patch(
        f"/build/v2/profiles/{profile_id}/configurations/{configuration_id}",
        configuration_data,
    )


def delete_build_configuration(profile_id, configuration_id):
    """Delete build configuration"""
    return get_api().delete(
        f"/build/v2/profiles/{profile_id}/configurations/{configuration_id}"
    )


def get_build_configuration_details(profile_id, configuration_id):
    """Get detailed information about a build configuration"""
    return get_api().get(
        f"/build/v2/profiles/{profile_id}/configurations/{configuration_id}"
    )
