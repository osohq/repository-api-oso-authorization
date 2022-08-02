#!/usr/bin/python3
from dataclasses import dataclass

@dataclass
class User:
    id: str

@dataclass
class Repository:
    id: str

class RepositoryRoles:
    OWNER = "owner"
    ADMIN = "admin"
    GUEST = "guest"

class RepositoryPermissions:
    LIST_DIRECTORIES = "list_directory"
    CREATE_DIRECTORY = "create_directory"
    DOWNLOAD_FILE = "download_file"
    UPLOAD_FILE = "upload_file"
