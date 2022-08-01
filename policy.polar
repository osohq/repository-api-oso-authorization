# Define all actor types.
actor User { }

# Define all resource types
resource Repository {
    # Define all permission types that are allowed on Repository objects.
    permissions = [
        "list_directory",
        "create_directory",
        "download_file",
        "upload_file"
    ];

    # Define all available roles an actor can have on a Repository object.
    roles = ["owner", "admin", "guest"];

    # Define all permission/role assignments.
    "list_directory" if "guest";
    "download_file" if "guest";

    "list_directory" if "admin";
    "create_directory" if "admin";
    "download_file" if "admin";
    "upload_file" if "admin";

    "admin" if "owner";
}


