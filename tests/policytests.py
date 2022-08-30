#!/usr/bin/python3
import os
import oso_cloud
import sys
import unittest

# Make sure to call all the tests from the parent directory.
sys.path.append(os.getcwd())
import osoenvconfig
import policydefinitions

_oso_client = None

# Test the expected behavior of the Oso Policy specified in the project.
class AccessPolicyFunctionalTests(unittest.TestCase):
    def setUp(self):
        log_message = "Performing Test ::{}".format(self._testMethodName)
        print("INFO: policytests", log_message)

    def test_role_admin(self):
        # Create an actor and resource with an assigned role.
        test_user = {
            "type": "User",
            "id": "user@test-role-admin"
        }
        test_user_repo = {
            "type": "Repository",
            "id": "test-role-admin"
        }
        assigned_role = policydefinitions.RepositoryRoles.ADMIN
        _oso_client.tell(
            "has_role",
            test_user,
            assigned_role,
            test_user_repo)

        # Expected TRUE authorizations for "owner" permissions.
        self.assertTrue(_oso_client.authorize(
            test_user,
            policydefinitions.RepositoryPermissions.LIST_DIRECTORIES,
            test_user_repo))

        self.assertTrue(_oso_client.authorize(
            test_user,
            policydefinitions.RepositoryPermissions.DOWNLOAD_FILE,
            test_user_repo))

        self.assertTrue(_oso_client.authorize(
            test_user,
            policydefinitions.RepositoryPermissions.CREATE_DIRECTORY,
            test_user_repo))

        self.assertTrue(_oso_client.authorize(
            test_user,
            policydefinitions.RepositoryPermissions.UPLOAD_FILE,
            test_user_repo))

        return None

    def test_role_owner(self):
        # Create an actor and resource with an assigned role.

        test_user = {
            "type": "User",
            "id": "user@test-role-owner"
        }
        test_user_repo = {
            "type": "Repository",
            "id": "test-role-owner"
        }
        assigned_role = policydefinitions.RepositoryRoles.OWNER
        _oso_client.tell(
            "has_role",
            test_user,
            assigned_role,
            test_user_repo)

        # Expected TRUE authorizations for "owner" permissions.
        self.assertTrue(_oso_client.authorize(
            test_user,
            policydefinitions.RepositoryPermissions.LIST_DIRECTORIES,
            test_user_repo))

        self.assertTrue(_oso_client.authorize(
            test_user,
            policydefinitions.RepositoryPermissions.DOWNLOAD_FILE,
            test_user_repo))

        self.assertTrue(_oso_client.authorize(
            test_user,
            policydefinitions.RepositoryPermissions.CREATE_DIRECTORY,
            test_user_repo))

        self.assertTrue(_oso_client.authorize(
            test_user,
            policydefinitions.RepositoryPermissions.UPLOAD_FILE,
            test_user_repo))

        return None

    def test_role_guest(self):
        # Create an actor and resource with an assigned role.
        test_user = {
            "type": "User",
            "id": "user@test-role-guest"
        }
        test_user_repo = {
            "type": "Repository",
            "id": "test-role-guest"
        }
        assigned_role = policydefinitions.RepositoryRoles.GUEST
        _oso_client.tell(
            "has_role",
            test_user,
            assigned_role,
            test_user_repo)

        # Expected TRUE authorizations for "guest" permissions.
        self.assertTrue(_oso_client.authorize(
            test_user,
            policydefinitions.RepositoryPermissions.LIST_DIRECTORIES,
            test_user_repo))

        self.assertTrue(_oso_client.authorize(
            test_user,
            policydefinitions.RepositoryPermissions.DOWNLOAD_FILE,
            test_user_repo))

        # Expected FALSE authorizations for "guest" permissions.
        self.assertFalse(_oso_client.authorize(
            test_user,
            policydefinitions.RepositoryPermissions.CREATE_DIRECTORY,
            test_user_repo))

        self.assertFalse(_oso_client.authorize(
            test_user,
            policydefinitions.RepositoryPermissions.UPLOAD_FILE,
            test_user_repo))

        return None

if __name__ == "__main__":
    try:
        # Configure the Oso Cloud test environment before each run
        # of the policy tests:
        # 1. Clear the environment before running tests:
        # osoenvconfig.clear_environment()
        # 2. Upload the most recent policy to Oso Cloud
        osoenvconfig.load_policy("policy.polar")

        # Authenticate the connection to Oso Cloud.
        host_api_key = os.environ.get("OSO_AUTH")
        _oso_client = oso_cloud.Oso(
            url="https://cloud.osohq.com",
            api_key=host_api_key)

        # Run the tests.
        unittest.main()

    except SystemExit as error:
        if error.args[0] == True:
            raise