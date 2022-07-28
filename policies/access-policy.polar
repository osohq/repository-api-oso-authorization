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
    roles = ["owner", "admin"];

    # Create permission/role assignments
    "list_directory" if "owner";
    "list_directory" if "admin";

    "create_directory" if "owner";
    "create_directory" if "admin";
    
    "download_file" if "owner";
    "download_file" if "admin";
    
    "upload_file" if "owner";
    "upload_file" if "admin";
}


