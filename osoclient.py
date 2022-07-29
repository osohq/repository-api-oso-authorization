#!/usr/bin/python3
import logging
import os
from oso_cloud import Oso


class OsoClientUtil:
    _ENV_VAR_OSO_AUTH_NAME = "OSO_AUTH"
    def __init__(self):
        # Retreive the api-key from the host machine.
        host_api_key = os.environ[OsoClientUtil._ENV_VAR_OSO_AUTH_NAME]
        self._oso = None
        if host_api_key == None:
            host_api_key = ""
            log_message = "Can not create a new Oso client object. A valid Oso API key could not be retrieved from the host."
            logging.error(log_message)
        else:
            self._oso = Oso(url="https://cloud.osohq.com", api_key=host_api_key)

    def load_policy(self, policy_file_name):
        api_result = None
        with open(policy_file_name) as policy_file:
            policy_string = policy_file.read()
            api_result = self._oso.policy(policy=policy_string)
        return api_result

    def get_client(self):
        return self._oso

    def has_role(self, actor, role, resource):
        oso_facts = self._oso.get(
            "has_role",
            actor,
            role,
            resource)

        # No validation is performed on the returned facts.
        return (isinstance(oso_facts, list) and len(oso_facts) == 1)


if __name__ == "__main__":
    oso_client = OsoClientUtil().get_client()
