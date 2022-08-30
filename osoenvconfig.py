#!/usr/bin/python3
import os
import oso_cloud

def clear_environment():
    try:
        # Authenticate the connection to Oso Cloud.
        host_api_key = os.environ.get("OSO_AUTH")
        oso_client = oso_cloud.Oso(
            url="https://cloud.osohq.com",
            api_key=host_api_key)

        # Clear any existing data in Oso Cloud.
        oso_client.api.clear_data()

    except Exception as e:
        print(e)

    return None

def load_policy(policy_file_name="policy.polar"):
    try:
        # Authenticate the connection to Oso Cloud.
        host_api_key = os.environ.get("OSO_AUTH")
        oso_client = oso_cloud.Oso(
            url="https://cloud.osohq.com",
            api_key=host_api_key)
        # Load the Polar authorization policy into Oso Cloud.
        with open(policy_file_name) as policy_file:
            policy_string = policy_file.read()
            oso_client.policy(policy=policy_string)

    except Exception as e:
        print(e)

    return None

if __name__ == "__main__":
    ###############################################################################
    # Configure the Oso Cloud Environment
    ###############################################################################
    clear_environment()
    load_policy()
