#!/usr/bin/python3
from dataclasses import dataclass

@dataclass
class User:
    id: str

@dataclass
class Group:
    id: str

@dataclass
class Repository:
    id: str

class RoleTypes:
    OWNER = "owner"
    ADMIN = "admin"

class PermissionTypes:
    LIST_DIRECTORY = "list_directory"
    CREATE_DIRECTORY = "create_directory"
    DOWNLOAD_FILE = "download_file"
    UPLOAD_FILE = "upload_file"
