# Define all actor types.
actor User { }

# Define all resource types
resource Repository {
    # Define all permission types that are allowed on Repository objects.
    permissions = [
        "list_directories",
        "create_directory",
        "download_file",
        "upload_file"
    ];

    # Define all available roles an actor can have on a Repository object.
    roles = ["owner", "admin", "guest"];

     # Define all permission/role assignments.
    "list_directories" if "guest";
    "download_file" if "guest";

    "list_directories" if "admin";
    "create_directory" if "admin";
    "download_file" if "admin";
    "upload_file" if "admin";

    # An "owner" has ALL "admin" roles.
    "admin" if "owner";
}