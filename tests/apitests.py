#!/usr/bin/python3
import os
import requests
import sys
import time
import unittest

# Make sure to call all the tests from the parent directory.
sys.path.append(os.getcwd())
import repohostutils

from repohostutils import ApiRoutes
from repohostutils import ApiParameterKeys
from repohostutils import HttpResponseCode


_TMP_DIR = ".tmp"

class _HelperFunctions:
    @staticmethod
    def create_repo(username, repo_name):
        # Create the API Request URL
        api_request_url = repohostutils.localhost_api_endpoint(ApiRoutes.CREATE_REPO)

        # Form the HTTP request.
        http_headers = {
            'Content-Type': "application/json",
        }
        content_data = {
            ApiParameterKeys.USERNAME: username,
            ApiParameterKeys.REPO_NAME: repo_name
        }
        http_response = requests.post(
            api_request_url,
            headers=http_headers,
            json=content_data
        )
        return http_response

    def create_directory(username, repo_name, directory_path):
        # Create the API Request URL
        api_request_url = repohostutils.localhost_api_endpoint(ApiRoutes.CREATE_DIRECTORY)

        # Form the HTTP request.
        http_headers = {
            'Content-Type': "application/json",
        }
        content_data = {
            ApiParameterKeys.USERNAME: username,
            ApiParameterKeys.REPO_NAME: repo_name,
            ApiParameterKeys.DIRECTORY_PATH: directory_path
        }
        http_response = requests.post(
            api_request_url,
            headers=http_headers,
            json=content_data
        )

        return http_response

class RepoAccessFunctionalTests(unittest.TestCase):
    def setUp(self):
        log_message = "Performing Test ::{}".format(self._testMethodName)
        print("INFO: apitests", log_message)

    def test_create_repo(self):
        username = "user@test-create-repo"
        repo_name = "test-create-repo"
        http_response = _HelperFunctions.create_repo(
            username,
            repo_name
        )

        self.assertEqual(
            HttpResponseCode.SUCCESSFUL_RESPONSE_200_OK,
            http_response.status_code)
        return None

    def test_create_directory(self):
        # Create a repo for the test.
        # The user will own the associated repository specified in the request.
        username = "user@test-create-directory"
        repo_name = "test-create-directory"
        http_response = _HelperFunctions.create_repo(
            username,
            repo_name
        )

        # Create a new directory in the repo.
        directory_path = "test-directory"
        http_response = _HelperFunctions.create_directory(
            username,
            repo_name,
            directory_path
        )

        # Validate a successful HTTP response from the server.
        self.assertEqual(
            HttpResponseCode.SUCCESSFUL_RESPONSE_200_OK,
            http_response.status_code)
        return None

    def test_list_directories(self):
        # Create a repo for the test.
        # The user will own the associated repository specified in the request.
        username = "user@test-list-directories"
        repo_name = "test-list-directories"
        http_response = _HelperFunctions.create_repo(
            username,
            repo_name
        )

        # Create several directories in the repo.
        # Keep a list of all sub directory names for later validation.
        test_directories = []
        number_test_directories = 5
        for i in range(0, number_test_directories):
            directory_path = "test-directory-{}".format(i)
            _HelperFunctions.create_directory(
                username,
                repo_name,
                directory_path
            )

        # Create the API Request URL
        api_request_url = repohostutils.localhost_api_endpoint(ApiRoutes.LIST_DIRECTORIES)

        # Form the HTTP request.
        http_headers = {
            'Content-Type': "application/json",
        }
        content_data = {
            ApiParameterKeys.USERNAME: username,
            ApiParameterKeys.REPO_NAME: repo_name
        }
        http_response = requests.get(
            api_request_url,
            headers=http_headers,
            json=content_data
        )

        # Validate a successful HTTP response from the server.
        self.assertEqual(
            HttpResponseCode.SUCCESSFUL_RESPONSE_200_OK,
            http_response.status_code)

        # Retrieve the request data 'subdirectories'
        response_data = http_response.json()
        subdirectories = response_data.get('subdirectories')

        # Perform a simple validation that the expected number of
        # subdirectories is present in the repo.
        self.assertNotEqual(
            subdirectories,
            None)

        self.assertEqual(
            len(subdirectories),
            number_test_directories
        )

        return None

    def test_upload_file(self):
        # Create a repo for the test.
        # The user will own the associated repository specified in the request.
        username = "user@test-upload_file"
        repo_name = "test-upload-file"
        http_response = _HelperFunctions.create_repo(
            username,
            repo_name
        )

        # Create a file to upload to the repo.
        file_name = "test-upload-file.bin"
        # Remote path relative to the root, repo directory.
        remote_file_path = "test-directory/{}".format(file_name)
        local_file_path = "{}/{}".format(_TMP_DIR, file_name)
        file_size_in_bytes = 1024
        write_mode = "wb"
        with open(local_file_path, write_mode) as f:
            f.write(os.urandom(file_size_in_bytes))

        # Create the API Request URL
        api_request_url = repohostutils.localhost_api_endpoint(ApiRoutes.UPLOAD_FILE)

        # Form the HTTP request.
        http_headers = {
            'Content-Type': "application/octet-stream",
        }
        content_data = {
            ApiParameterKeys.USERNAME: username,
            ApiParameterKeys.REPO_NAME: repo_name,
            ApiParameterKeys.FILE_NAME: file_name,
            ApiParameterKeys.DIRECTORY_PATH: remote_file_path,
            ApiParameterKeys.WRITE_MODE: write_mode
        }
        # Open the file to upload in the HTTP request.
        with open(local_file_path, "rb") as f:
            http_response = requests.put(
                api_request_url,
                headers=http_headers,
                params=content_data,
                data=f
            )

        # Validate a successful HTTP response from the server.
        self.assertEqual(
            HttpResponseCode.SUCCESSFUL_RESPONSE_201_CREATED,
            http_response.status_code)

    def test_download_file(self):
        # Create a repo for the test.
        # The user will own the associated repository specified in the request.
        username = "user@test-download-file"
        repo_name = "test-download-file"
        http_response = _HelperFunctions.create_repo(
            username,
            repo_name
        )

        # Create a file in the new user repo.
        # Save the contents of the file for later validation.
        # Note: Here we use the API helper functions directly
        #       and do not go through the REST API.
        test_file_extension = "txt"
        repo_directory_path = "."
        repo_file_name = "test-file.{}".format(test_file_extension)
        test_file_content = time.asctime()
        repohostutils.write_file(
            username=username,
            repo_name=repo_name,
            directory_path=repo_directory_path,
            file_name=repo_file_name,
            file_data=test_file_content
        )

        # Create the API Request URL
        api_request_url = repohostutils.localhost_api_endpoint(ApiRoutes.DOWNLOAD_FILE)

        # Form the HTTP request.
        http_headers = {
            'Content-Type': "application/json",
        }
        content_data = {
            ApiParameterKeys.USERNAME: username,
            ApiParameterKeys.REPO_NAME: repo_name,
            ApiParameterKeys.FILE_PATH: repo_file_name
        }
        http_response = requests.get(
            api_request_url,
            headers=http_headers,
            json=content_data,
            stream=True
        )

        # Since we have only written a small amount of data,
        # we can compare the contents in memory.
        downloaded_file_content = http_response.content.decode('utf-8')
        self.assertEqual(
            test_file_content,
            downloaded_file_content
        )

        self.assertEqual(
            HttpResponseCode.SUCCESSFUL_RESPONSE_200_OK,
            http_response.status_code)
        return None


if __name__ == "__main__":
    try:
        #######################################################################
        # Configure the test environment
        if not os.path.exists(_TMP_DIR):
            os.mkdir(_TMP_DIR)

        # Run the tests.
        unittest.main()

    except SystemExit as error:
        if error.args[0] == True:
            raise