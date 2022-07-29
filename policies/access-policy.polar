actor User { }

resource Repository {
    # List all permission types that are allowed on Repository objects
    permissions = [
        "list_directory",
        "create_directory",
        "download_file",
        "upload_file"
    ];

    # List all available roles an actor in the set [User, Group]
    # can have on a Repository object.
    roles = ["owner", "admin", "guest"];

    # Create permission/role assignments
    "list_directory" if "guest";
    "download_file" if "guest";

    "list_directory" if "admin";
    "create_directory" if "admin";
    "download_file" if "admin";
    "upload_file" if "admin";

    "guest" if "admin";
    "admin" if "owner";
}


