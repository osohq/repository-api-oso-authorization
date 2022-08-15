# Getting Started
This application is built using Flask and the `oso_cloud` Python client. It implements selected behaviors of a file repository system and exposes them through a REST API. The main goal of this application is to demonstrate how Oso Cloud can be used to model, manage, and enforce authorization.

> __*NOTE*__: Running this application and its tests requires permission to modify the host machine's directories (i.e. create files/folder, list files/directories). Please ensure that the proper permissions and access are given to the application.

You can use this [Getting Started](#getting-started) guide to learn how to start and test the application's services. There is also a full description of *how* the application was built in the tutorial:
[Oso Cloud Authorization within a Repository REST API](https://cloud-docs.osohq.com/tutorials/authz-within-rest-apis).

More information about Oso Cloud, its tools and other resources can be found by visiting: https://cloud-docs.osohq.com/.

**Dependency Table**
| Dependency | Version Tested | Description |
|------------|----------------|-------------|
| `Flask` | 2.1.3 | Web microframework used for the REST API implementation. |
| `oso-cloud` | 0.7.0 | Oso Cloud Python client used for managing authorization within the web application.
| `Python` | 3.9.13 | Programming language used for the web application implementation. |
| `requests` | 2.28.1 | HTTP library for testing communication with the web application's REST APIs. |

## Running the Application
Our web application is called `repoapis`. Start it by running the following commands in your terminal window.
```bash
export FLASK_APP=repoapis
export FLASK_ENV=development
flask run
```

After executing the commands, some information will be displayed in your terminal window about the session that is running.
```bash
 * Serving Flask app 'repoapis' (lazy loading)
 * Environment: development
 * Debug mode: on
 * Running on http://127.0.0.1:5000 (Press CTRL+C to quit)
 * Restarting with stat
 * Debugger is active!
 * Debugger PIN: ***-316
```

## Interacting with the REST APIs
Using the information returned when starting the application, find the section:
> Running on ...

to get the URL needed to reach the REST APIs. The application simply resolves `localhost` and in this example we find:
> `http://127.0.0.1:5000`

as our web address. You can now use this along with the API routes table below to interact with the `repoapis` application.

| API Route | HTTP Method | Request Body Schema | Key/Value Descriptions |
|-----------|-------------|---------------------|------------------------|
| `/create-repo` | `POST` | *application/json* | <span style="color:red">**required**</span> <br>&emsp; `username` *(string)* <br>&emsp; `repo_name` *(string)* |
| `/create-directory` | `POST` | *application/json* | <span style="color:red">**required**</span> <br>&emsp; `username` *(string)* <br>&emsp; `repo_name` *(string)* <br>&emsp; `directory_path` *(string)* |
| `/list-directories` | `GET` | *application/json* | <span style="color:red">**required**</span> <br>&emsp; `username` *(string)* <br>&emsp; `repo_name` *(string)* <br> **optional** <br>&emsp; `directory_path` *(string)* |
| `/download-file` | `GET` | *application/json* | <span style="color:red">**required**</span> <br>&emsp; `username` *(string)* <br>&emsp; `repo_name` *(string)*  <br>&emsp; `file_path` *(string)* <br> **optional** <br>&emsp; `downloaded_file_name` *(string)* |
| `/upload-file` | `PUT` | *application/json* | <span style="color:red">**required**</span> <br>&emsp; `username` *(string)* <br>&emsp; `repo_name` *(string)* <br>&emsp; `file_name` *(string)* <br> **optional** <br>&emsp; `directory_path` *(string)*  <br>&emsp; `write_mode` *(string)*|


## Running the API Test Script
Our application also comes with some functional tests that demonstrate how you can programmatically interact with the REST APIs. These tests are located in `./tests/repoapitests.py`. To run them, run this file from the top level project directory and call `./tests/repoapitests.py` from your terminal or IDE of preference.

In order for the tests to successfully run, the web application **must** be running. Please follow instructions in [Running the Application](#running-the-application) before proceeding.

In a new terminal window, run:
```bash
> python3 ./tests/repoapitests.py
```
The script will hit each REST API as described in the previous section: [Interacting with the REST APIs](#interacting-with-the-rest-apis). The output from this process should look like the following:
```bash
[INFO] Performing Test repoapitests.py::test_create_directory
.[INFO] Performing Test repoapitests.py::test_create_repo
.[INFO] Performing Test repoapitests.py::test_download_file
.[INFO] Performing Test repoapitests.py::test_list_directories
.[INFO] Performing Test repoapitests.py::test_upload_file
.
----------------------------------------------------------------------
Ran 5 tests in 2.716s

OK
```