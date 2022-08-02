#!/usr/bin/python3
import json
import os
import oso_cloud

from flask import Flask
from flask import jsonify
from flask import make_response
from flask import request
from flask import send_file

import repohostutils

from policydefinitions import RepositoryPermissions, RepositoryRoles, User, Repository
from repohostutils import ApiParameterKeys, ApiResponseKeys
from repohostutils import HttpResponseCode
from repohostutils import ParameterValidation

# Oso Cloud client object:
#   We will configure our Oso Cloud environment
#   at the bottom of the file before we run our
#   API services.
_oso_client = None

_app = Flask(__name__)

# This API route is controlled by the application provider.
# Users subscribed to this application have permission to create
# new repositories with their username. Oso Cloud manages the
# resources created thereafter (i.e. repositories, directories,
# files, ect...). Therefore, only Oso facts are created and
# and Oso Cloud authorization requests are NOT made within this
# API route.
@_app.route("/create-repo", methods=['POST'])
def create_repo():
    username = request.json.get(ApiParameterKeys.USERNAME)
    repo_name = request.json.get(ApiParameterKeys.REPO_NAME)

    # Check that the required parameters have been provided in the HTTP request.
    if (not ParameterValidation.check_required_str(ApiParameterKeys.USERNAME, username) or
        not ParameterValidation.check_required_str(ApiParameterKeys.REPO_NAME, repo_name)):
        return make_response(None, HttpResponseCode.CLIENT_ERROR_RESPONSE_400_BAD_REQUEST)

    response_json = None
    try:
        # Create an Oso fact for the actor:User/resource:Repository pair,
        # granting the role of "owner", to the User for the specified Repository.
        defined_role = RepositoryRoles.OWNER
        _oso_client.tell(
            "has_role",
            User(username),
            RepositoryRoles.OWNER,
            Repository(repo_name))
        # Create a new directory for the specified username/rep_name pair.
        relative_path = repohostutils.create_user_repo(username, repo_name)
        # Get the relative path of the repo as a JSON
        # for to the response back to the client.
        response_json = repohostutils.get_path_json(relative_path)
    except Exception as e:
        print(e)
        return make_response(None, HttpResponseCode.SERVER_ERROR_RESPONSE_500_INTERNAL_SERVER_ERROR)

    return make_response(response_json, HttpResponseCode.SUCCESSFUL_RESPONSE_200_OK)

@_app.route("/create-directory", methods=['POST'])
def create_directory():
    username = request.json.get(ApiParameterKeys.USERNAME)
    repo_name = request.json.get(ApiParameterKeys.REPO_NAME)
    directory_path = request.json.get(ApiParameterKeys.DIRECTORY_PATH)

    # Check that the required parameters have been provided in the HTTP request.
    if (not ParameterValidation.check_required_str(ApiParameterKeys.USERNAME, username) or
        not ParameterValidation.check_required_str(ApiParameterKeys.REPO_NAME, repo_name) or
        not ParameterValidation.check_required_str(ApiParameterKeys.DIRECTORY_PATH, directory_path)):
        return make_response(None, HttpResponseCode.CLIENT_ERROR_RESPONSE_400_BAD_REQUEST)

    response_json = None
    try:
        # Check Oso Cloud to ensure the specified User has permission to
        # create directories on the specified Repository object.
        if _oso_client.authorize(User(username),
                                 RepositoryPermissions.CREATE_DIRECTORY,
                                 Repository(repo_name)):
            relative_path = repohostutils.create_user_repo_directory(
                username,
                repo_name,
                directory_path)
            response_json = repohostutils.get_path_json(relative_path)
        else:
            return make_response(None, HttpResponseCode.CLIENT_ERROR_RESPONSE_401_UNAUTHORIZED)
    except Exception as e:
        print(e)
        return make_response(None, HttpResponseCode.SERVER_ERROR_RESPONSE_500_INTERNAL_SERVER_ERROR)

    return make_response(response_json, HttpResponseCode.SUCCESSFUL_RESPONSE_200_OK)

@_app.route("/list-directories", methods=['GET'])
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

    response_json = None
    try:
        # Check Oso Cloud to ensure the specified User has permission to
        # list directories from the specified Repository object.
        if _oso_client.authorize(User(username),
                                 RepositoryPermissions.LIST_DIRECTORIES,
                                 Repository(repo_name)):
            subdirectories = repohostutils.list_directories(
                username,
                repo_name,
                directory_path
            )
            # Generate the list of subdirectories to provide in the server response to the client.
            subdirectories_map = {
                ApiResponseKeys.SUBDIRECTORIES: subdirectories
            }
            response_json = jsonify(subdirectories_map)
        else:
            return make_response(None, HttpResponseCode.CLIENT_ERROR_RESPONSE_401_UNAUTHORIZED)
    except Exception as e:
        print(e)
        return make_response(None, HttpResponseCode.SERVER_ERROR_RESPONSE_500_INTERNAL_SERVER_ERROR)

    return make_response(response_json, HttpResponseCode.SUCCESSFUL_RESPONSE_200_OK)

@_app.route("/download-file", methods=['GET'])
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


    file_object = None
    file_object = None
    try:
        # Check Oso Cloud to ensure the specified User has permission to
        # download files from the specified Repository object.
        if _oso_client.authorize(User(username),
                                 RepositoryPermissions.DOWNLOAD_FILE,
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
        else:
            return make_response(None, HttpResponseCode.CLIENT_ERROR_RESPONSE_401_UNAUTHORIZED)
    except Exception as e:
        print(e)
        return make_response(None, HttpResponseCode.SERVER_ERROR_RESPONSE_500_INTERNAL_SERVER_ERROR)


    return send_file(
                file_object,
                mimetype=file_mimetype,
                as_attachment=True,
                download_name=download_file_name
    )

@_app.route("/upload-file", methods=['PUT'])
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

    json_response = None
    try:
        # Check Oso Cloud to ensure the specified User has permission to
        # upload files to the specified Repository object.
        if _oso_client.authorize(User(username),
                                 RepositoryPermissions.UPLOAD_FILE,
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
        else:
            return make_response(None, HttpResponseCode.CLIENT_ERROR_RESPONSE_401_UNAUTHORIZED)
    except Exception as e:
        print(e)
        return make_response(None, HttpResponseCode.SERVER_ERROR_RESPONSE_500_INTERNAL_SERVER_ERROR)

    return make_response(json_response, HttpResponseCode.SUCCESSFUL_RESPONSE_201_CREATED)


###############################################################################
# Configure the Oso Client
###############################################################################
try:
#   1. Retrieve the api-key from the host machine to authenticate API usage
#      with Oso Cloud. The environment variable where the Oso API key is
#      stored is "OSO_AUTH".
    host_api_key = os.environ.get("OSO_AUTH")
    _oso_client = oso_cloud.Oso(
        url="https://cloud.osohq.com",
        api_key=host_api_key)
#   2. Load the Polar authorization policy into Oso Cloud.
    policy_file_name = "policy.polar"
    with open(policy_file_name) as policy_file:
        policy_string = policy_file.read()
        _oso_client.policy(policy=policy_string)
except Exception as e:
        print(e)

###############################################################################
# Configure the host
###############################################################################
repohostutils.repo_host_init()

###############################################################################
# Run the API application
###############################################################################
_app.run(
    host=repohostutils.DEFAULT_HTTP_HOST_NAME,
    port=repohostutils.DEFAULT_HTTP_PORT_NUMBER
)