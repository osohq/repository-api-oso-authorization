#!/usr/bin/python3
import mimetypes
import os
import sys

from flask import jsonify


# HTTP Utils
class HttpResponseCode:
    SUCCESSFUL_RESPONSE_200_OK = 200
    SUCCESSFUL_RESPONSE_201_CREATED = 201
    SUCCESSFUL_RESPONSE_204_NO_CONTENT = 204

    CLIENT_ERROR_RESPONSE_400_BAD_REQUEST = 400
    CLIENT_ERROR_RESPONSE_401_UNAUTHORIZED = 401
    CLIENT_ERROR_RESPONSE_403_FORBIDDEN = 403
    CLIENT_ERROR_RESPONSE_404_NOT_FOUND = 404
    CLIENT_ERROR_RESPONSE_405_METHOD_NOT_ALLOWED = 405
    CLIENT_ERROR_RESPONSE_409_CONFLICT = 409
    CLIENT_ERROR_RESPONSE_429_TOO_MANY_REQUESTS = 429

    SERVER_ERROR_RESPONSE_500_INTERNAL_SERVER_ERROR = 500
    SERVER_ERROR_RESPONSE_503_SERVICE_UNAVAILABLE = 503

class ApiParameterKeys:
    USERNAME = "username"
    REPO_NAME = "repo_name"
    DIRECTORY_PATH = "directory_path"
    FILE_PATH = "file_path"
    FILE_NAME = "file_name"
    DOWNLOAD_FILE_NAME = "download_file_name"
    WRITE_MODE = "write_mode"

class ApiResponseKeys:
    SUBDIRECTORIES = "subdirectories"

class ParameterValidation:
    @staticmethod
    def check_required_str(parameter_name, parameter):
        if not isinstance(parameter, str):
            log_message = "'parameter_name' must be provided in the request."
            commonutils.log_error(log_message)
            return False
        return True

DEFAULT_HTTP_HOST_NAME = "localhost"
DEFAULT_HTTP_PORT_NUMBER = "5000"

def localhost_api_endpoint(api_requst):
    endpoint_url = None
    if isinstance(api_requst, str):
        endpoint_url = "http://{}:{}/{}".format(
            DEFAULT_HTTP_HOST_NAME,
            DEFAULT_HTTP_PORT_NUMBER,
            api_requst)
    return endpoint_url

APPLICATION_FOLDER_NAME = "repo-host-root"
# Only store the relative path from the application.
DEFAULT_HOST_WORKING_DIRECTORY = os.path.relpath(os.getcwd())

def _create_directory(path):
    current_folder_set = []
    if isinstance(path, str):
        path.replace("\\","/")
        if "/" == path[0]:
           current_folder_set.append("/")

        folders_in_path = path.split("/")
        for folder in folders_in_path:
            current_folder_set.append(folder)
            current_path = "/".join(current_folder_set)
            if not os.path.exists(current_path):
                os.mkdir(current_path)

    return None

def _create_file(file_path):
    file_name = None
    folders_in_path = file_path.split("/")
    if len(folders_in_path) > 0:
        file_name = folders_in_path[-1]
        folders_in_path = folders_in_path[:-1]
    file_directory = "/".join(folders_in_path)
    _create_directory(file_directory)
    with open(file_path, "w") as f:
        pass

    return file_path

def _application_root_directory():
    working_directory = DEFAULT_HOST_WORKING_DIRECTORY
    return "{}/{}".format(
        working_directory,
        APPLICATION_FOLDER_NAME
    )

def _get_user_directory(username):
    root_directory = _application_root_directory()
    return "{}/{}".format(root_directory, username)

def _get_user_repo_path(username, repo_name):
    return "{}/{}".format(
        _get_user_directory(username),
        repo_name
    )

def _get_user_repo_resource_path(username, repo_name, resource_path):
    user_repo_directory = _get_user_repo_path(username, repo_name)
    return "{}/{}".format(user_repo_directory, resource_path)

def get_file_name_from_path(file_path):
    file_name = None
    if (isinstance(file_path, str) and file_path != ""):
        file_path = file_path.replace("\\", "/")
        file_name = file_path.split("/")[-1]

    return file_name

def get_path_json(path):
    return jsonify({
        "path": path
    })

def repo_host_init():
    root_directory = _application_root_directory()
    _create_directory(root_directory)

    return None

def create_user_repo(username, repo_name):
    user_repo_directory = _get_user_repo_path(username, repo_name)
    _create_directory(user_repo_directory)
    return repo_name

def create_user_repo_directory(username, repo_name, directory_path):
    full_directory_path = _get_user_repo_resource_path(
        username,
        repo_name,
        directory_path)

    _create_directory(full_directory_path)

    return "{}/{}".format(repo_name, directory_path)

def create_user_repo_file(username, repo_name, file_path):
    full_file_path = _get_user_repo_resource_path(
        username,
        repo_name,
        file_path)

    _create_file(full_file_path)

    return "{}/{}".format(repo_name, file_path)

def list_directories(username, repo_name, directory_path):
    full_directory_path = _get_user_repo_resource_path(
        username,
        repo_name,
        directory_path)

    subdirectories = None
    if os.path.exists(full_directory_path):
        subdirectories = [obj.path for obj in os.scandir(full_directory_path) if obj.is_dir()]

    return subdirectories

def write_file(username,
               repo_name,
               directory_path,
               file_name,
               file_data,
               write_mode="w"):
    file_path = "{}/{}".format(
        directory_path,
        file_name
    )

    full_file_path = _get_user_repo_resource_path(
        username,
        repo_name,
        file_path)

    _create_file(full_file_path)

    # Fill the file with the contents of file_data
    with open(full_file_path, write_mode) as f:
        f.write(file_data)

    return "{}/{}".format(repo_name, file_path)

def open_read_only_file(username,
                        repo_name,
                        file_path):
    full_file_path = _get_user_repo_resource_path(
        username,
        repo_name,
        file_path)

    file_object = None
    if os.path.exists(full_file_path):
        file_object = open(full_file_path, "rb")
    else:
        log_message = "The requested file could not be found.\n"
        log_message += "{}: does not exist.".format(file_path)

    return file_object

def get_file_mimetype(username, repo_name, file_path):
    full_file_path = _get_user_repo_resource_path(
        username,
        repo_name,
        file_path)

    (mimetype_str, _) = mimetypes.guess_type(full_file_path)

    return mimetype_str