#!/usr/bin/python3
import json

from flask import Flask
from flask import jsonify
from flask import make_response
from flask import request
from flask import send_file

# Modules defined within this project.
import commonutils
import osoclient
import repohostutils

from policydefinitions import PermissionTypes, RoleTypes, User, Repository
from repohostutils import ApiRoutes
from repohostutils import ApiParameterKeys, ApiResponseKeys
from repohostutils import HttpResponseCode
from repohostutils import ParameterValidation


_webapp = Flask(__name__)

# Define paths to the Oso policies to use for authorization
# in the application.
DEFAULT_POLICIES_PATH = commonutils.policies_directory_path()
DEFAULT_POLICY_NAME = "access-policy.polar"

_oso_client_util = osoclient.OsoClientUtil()

# This API route is controlled by the application provider.
# Users subscribed to this application have permission to create
# new repositories with their username. Oso Cloud manages the
# resources created thereafter (i.e. repositories, directories,
# files, ect...). Therefore, only Oso facts are created and
# and Oso Cloud authorization requests are NOT made within this
# API route.
@_webapp.route(ApiRoutes.CREATE_REPO, methods=['POST'])
def create_repo():
    username = request.json.get(ApiParameterKeys.USERNAME)
    repo_name = request.json.get(ApiParameterKeys.REPO_NAME)
    
    # Check that the required parameters have been provided in the HTTP request.
    if (not ParameterValidation.check_required_str(ApiParameterKeys.USERNAME, username) or
        not ParameterValidation.check_required_str(ApiParameterKeys.REPO_NAME, repo_name)):
        return make_response(None, HttpResponseCode.CLIENT_ERROR_RESPONSE_400_BAD_REQUEST)

    # Retrieve the Oso client from the utility function.
    oso_client = _oso_client_util.get_client()

    # Create an Oso fact for the actor:User/resource:Repository pair,
    # granting the role of "owner", to the User for the specified Repository.
    defined_role = RoleTypes.OWNER
    oso_client.tell(
        "has_role",
        User(username),
        RoleTypes.OWNER,
        Repository(repo_name))

    # Verify that the new fact has been created in Oso Cloud for the
    # (User, Role, Repository) set, that was specified in the Oso tell command.
    oso_facts = oso_client.get(
            "has_role",
            User(username),
            defined_role,
            Repository(repo_name))

    # Verify that one and ONLY one Oso fact is returned.
    # We omit checking the contents of the Oso fact in this example
    # and rely on the existance of the fact as a sufficient criteria
    # for creating a new repo on the server for the specified user.
    if (isinstance(oso_facts, list) and len(oso_facts) == 1):
        # Create a new directory for the specified username/rep_name pair.
        relative_path = repohostutils.create_user_repo(username, repo_name)
        # Get the relative path of the repo as a JSON
        # for to the response back to the client.
        repsonse_json = repohostutils.get_path_json(relative_path)
        return make_response(repsonse_json, HttpResponseCode.SUCCESSFUL_RESPONSE_200_OK)

    # If one and ONLY one fact is not able to be retrieved from Oso Cloud,
    # then no resources are created on the server and return with an error.
    return make_response(None, HttpResponseCode.SERVER_ERROR_RESPONSE_500_INTERNAL_SERVER_ERROR)

@_webapp.route(ApiRoutes.CREATE_DIRECTORY, methods=['POST'])
def create_directory():
    username = request.json.get(ApiParameterKeys.USERNAME)
    repo_name = request.json.get(ApiParameterKeys.REPO_NAME)
    directory_path = request.json.get(ApiParameterKeys.DIRECTORY_PATH)

    # Check that the required parameters have been provided in the HTTP request.
    if (not ParameterValidation.check_required_str(ApiParameterKeys.USERNAME, username) or
        not ParameterValidation.check_required_str(ApiParameterKeys.REPO_NAME, repo_name) or
        not ParameterValidation.check_required_str(ApiParameterKeys.DIRECTORY_PATH, directory_path)):
        return make_response(None, HttpResponseCode.CLIENT_ERROR_RESPONSE_400_BAD_REQUEST)

    # Retrieve the Oso client from the utility function.
    oso_client = _oso_client_util.get_client()

    # Verify that the user is authorized to put files on this repo.
    try:
        # Check Oso Cloud to ensure the specified User has permission to
        # create directories on the specified Repository object.
        if oso_client.authorize(User(username),
                                PermissionTypes.CREATE_DIRECTORY,
                                Repository(repo_name)):
            relative_path = repohostutils.create_user_repo_directory(
                username,
                repo_name,
                directory_path)
            repsonse_json = repohostutils.get_path_json(relative_path)
            return make_response(repsonse_json, HttpResponseCode.SUCCESSFUL_RESPONSE_200_OK)
        else:
            return make_response(None, HttpResponseCode.CLIENT_ERROR_RESPONSE_401_UNATHORIZED)
    except Exception as e:
        print(e)

    return make_response(None, HttpResponseCode.SERVER_ERROR_RESPONSE_500_INTERNAL_SERVER_ERROR)

@_webapp.route(ApiRoutes.LIST_DIRECTORIES, methods=['GET'])
def list_directories():
    username = request.json.get(ApiParameterKeys.USERNAME)
    repo_name = request.json.get(ApiParameterKeys.REPO_NAME)
    directory_path = request.json.get(ApiParameterKeys.DIRECTORY_PATH)
    if None == directory_path:
        directory_path = "."

    # Check that the required parameters have been provided in the HTTP request.
    if (not ParameterValidation.check_required_str(ApiParameterKeys.USERNAME, username) or
        not ParameterValidation.check_required_str(ApiParameterKeys.REPO_NAME, repo_name) or
        not ParameterValidation.check_required_str(ApiParameterKeys.DIRECTORY_PATH, directory_path)):
        return make_response(None, HttpResponseCode.CLIENT_ERROR_RESPONSE_400_BAD_REQUEST)

    oso_client = _oso_client_util.get_client()
    try:
        # Check Oso Cloud to ensure the specified User has permission to
        # list directories from the specified Repository object.
        if oso_client.authorize(User(username),
                                PermissionTypes.LIST_DIRECTORY,
                                Repository(repo_name)):
            subdirectories = repohostutils.list_directories(
                username,
                repo_name,
                directory_path
            )
            # Return the list of subdirectories in the server response to the client.
            subdirectories_map = {
                ApiResponseKeys.SUBDIRECTORIES: subdirectories
            }
            return make_response(jsonify(subdirectories_map), HttpResponseCode.SUCCESSFUL_RESPONSE_200_OK)
        else:
            return make_response(None, HttpResponseCode.CLIENT_ERROR_RESPONSE_401_UNATHORIZED)
    except Exception as e:
        print(e)

    return make_response(None, HttpResponseCode.SERVER_ERROR_RESPONSE_500_INTERNAL_SERVER_ERROR)

@_webapp.route(ApiRoutes.DOWNLOAD_FILE, methods=['GET'])
def download_file():
    username = request.json.get(ApiParameterKeys.USERNAME)
    repo_name = request.json.get(ApiParameterKeys.REPO_NAME)
    file_path = request.json.get(ApiParameterKeys.FILE_PATH)
    download_file_name = request.json.get(ApiParameterKeys.DOWNLOAD_FILE_NAME)
    if None == download_file_name:
        download_file_name = repohostutils.get_file_name_from_path(file_path)

    # Check that the required parameters have been provided in the HTTP request.
    if (not ParameterValidation.check_required_str(ApiParameterKeys.USERNAME, username) or
        not ParameterValidation.check_required_str(ApiParameterKeys.REPO_NAME, repo_name) or
        not ParameterValidation.check_required_str(ApiParameterKeys.FILE_PATH, file_path)):
        return make_response(None, HttpResponseCode.CLIENT_ERROR_RESPONSE_400_BAD_REQUEST)
    
    oso_client = _oso_client_util.get_client()
    try:
        # Check Oso Cloud to ensure the specified User has permission to
        # download files from the specified Repository object.
        if oso_client.authorize(User(username),
                                PermissionTypes.DOWNLOAD_FILE,
                                Repository(repo_name)):
            file_mimetype = repohostutils.get_file_mimetype(
                username,
                repo_name,
                file_path
            )
            file_object = repohostutils.open_read_only_file(
                username,
                repo_name,
                file_path
            )
            return send_file(
                file_object,
                mimetype=file_mimetype,
                as_attachment=True,
                download_name=download_file_name
            )
        else:
            return make_response(None, HttpResponseCode.CLIENT_ERROR_RESPONSE_401_UNATHORIZED)
    except Exception as e:
        print(e)

    return make_response(None, HttpResponseCode.SERVER_ERROR_RESPONSE_500_INTERNAL_SERVER_ERROR)

@_webapp.route(ApiRoutes.UPLOAD_FILE, methods=['PUT'])
def upload_file():
    username = request.args.get(ApiParameterKeys.USERNAME)
    repo_name = request.args.get(ApiParameterKeys.REPO_NAME)
    file_name = request.args.get(ApiParameterKeys.FILE_NAME)
    directory_path = request.args.get(ApiParameterKeys.DIRECTORY_PATH)
    write_mode = request.args.get(ApiParameterKeys.WRITE_MODE)
    if None == directory_path:
        directory_path = "."

    if None == write_mode:
        write_mode = "wb"

    # Check that the required parameters have been provided in the HTTP request.
    if (not ParameterValidation.check_required_str(ApiParameterKeys.USERNAME, username) or
        not ParameterValidation.check_required_str(ApiParameterKeys.REPO_NAME, repo_name) or
        not ParameterValidation.check_required_str(ApiParameterKeys.FILE_NAME, file_name) or
        not ParameterValidation.check_required_str(ApiParameterKeys.DIRECTORY_PATH, directory_path)):
        return make_response(None, HttpResponseCode.CLIENT_ERROR_RESPONSE_400_BAD_REQUEST)

    oso_client = _oso_client_util.get_client()
    try:
        # Check Oso Cloud to ensure the specified User has permission to
        # upload files to the specified Repository object.
        if oso_client.authorize(User(username),
                                PermissionTypes.UPLOAD_FILE,
                                Repository(repo_name)):
            relative_path = repohostutils.write_file(
                username,
                repo_name,
                directory_path,
                file_name,
                request.data,
                write_mode=write_mode
            )
            json_response = repohostutils.get_path_json(relative_path)
            return make_response(json_response, HttpResponseCode.SUCCESSFUL_RESPONSE_201_CREATED)
        else:
            return make_response(None, HttpResponseCode.CLIENT_ERROR_RESPONSE_401_UNATHORIZED)
    except Exception as e:
        print(e)
    return make_response(None, HttpResponseCode.SERVER_ERROR_RESPONSE_500_INTERNAL_SERVER_ERROR)


# Load the current policy for testing.
OSO_POLICIES_PATH = commonutils.policies_directory_path()
OSO_POLICY_NAME = "access-policy.polar"
if isinstance(_oso_client_util, osoclient.OsoClientUtil):
    policy_file_name = "{}/{}".format(
        OSO_POLICIES_PATH,
        OSO_POLICY_NAME
    )
    api_result = _oso_client_util.load_policy(policy_file_name)

repohostutils.repo_host_init()

_webapp.run(
    host=repohostutils.DEFAULT_HTTP_HOST_NAME,
    port=repohostutils.DEFAULT_HTTP_PORT_NUMBER
)