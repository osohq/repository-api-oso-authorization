#!/usr/bin/python3
import os
import sys
import unittest

# Modules defined within this project.
# Make sure to call all the tests from the parent directory.
sys.path.append(os.getcwd())
import commonutils
import osoclient
import policydefinitions

from policydefinitions import User, Repository

MODULE_NAME = "access_policy_tests"
TEST_POLICIES_PATH = commonutils.policies_directory_path()
TEST_POLICY_NAME = "access-policy.polar"

_oso_client_util = osoclient.OsoClientUtil()

# Test the expected behavior of the Oso Policy specified in the project.
class AccessPolicyFunctionalTests(unittest.TestCase):
    def setUp(self):
        log_message = "Performing Test ::{}".format(self._testMethodName)
        commonutils.log_info(MODULE_NAME, log_message)

    def test_role_owner(self):
        oso_client = _oso_client_util.get_client()
        # Create an actor and resource with an assigned role.
        test_user = User("user@test-role-owner")
        test_user_repo = Repository("test-role-owner")
        assigned_role = policydefinitions.RoleTypes.OWNER
        oso_client.tell(
            "has_role",
            test_user,
            assigned_role,
            test_user_repo)

        # Expected TRUE authorizations for "owner" permissions.
        self.assertTrue(oso_client.authorize(
            test_user,
            policydefinitions.PermissionTypes.LIST_DIRECTORY,
            test_user_repo))

        self.assertTrue(oso_client.authorize(
            test_user,
            policydefinitions.PermissionTypes.DOWNLOAD_FILE,
            test_user_repo))

        self.assertTrue(oso_client.authorize(
            test_user,
            policydefinitions.PermissionTypes.CREATE_DIRECTORY,
            test_user_repo))

        self.assertTrue(oso_client.authorize(
            test_user,
            policydefinitions.PermissionTypes.UPLOAD_FILE,
            test_user_repo))

        return None

    def test_role_guest(self):
        oso_client = _oso_client_util.get_client()
        # Create an actor and resource with an assigned role.
        test_user = User("user@test-role-guest")
        test_user_repo = Repository("test-role-guest")
        assigned_role = policydefinitions.RoleTypes.GUEST
        oso_client.tell(
            "has_role",
            test_user,
            assigned_role,
            test_user_repo)

        # Expected TRUE authorizations for "guest" permissions.
        self.assertTrue(oso_client.authorize(
            test_user,
            policydefinitions.PermissionTypes.LIST_DIRECTORY,
            test_user_repo))

        self.assertTrue(oso_client.authorize(
            test_user,
            policydefinitions.PermissionTypes.DOWNLOAD_FILE,
            test_user_repo))

        # Expected FALSE authorizations for "guest" permissions.
        self.assertFalse(oso_client.authorize(
            test_user,
            policydefinitions.PermissionTypes.CREATE_DIRECTORY,
            test_user_repo))

        self.assertFalse(oso_client.authorize(
            test_user,
            policydefinitions.PermissionTypes.UPLOAD_FILE,
            test_user_repo))

        return None

if __name__ == "__main__":
    try:
        # Load the current policy for testing.
        if isinstance(_oso_client_util, osoclient.OsoClientUtil):
            policy_file_name = "{}/{}".format(
                TEST_POLICIES_PATH,
                TEST_POLICY_NAME
            )
            api_result = _oso_client_util.load_policy(policy_file_name)
        # Run the module's unit test.
        unittest.main()

    except SystemExit as error:
        if error.args[0] == True:
            raise