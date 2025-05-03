import os


def delete_migration_files_except_init(base_dir):
    # Loop through each app directory in 'app/'
    for app_name in os.listdir(base_dir):
        app_path = os.path.join(base_dir, app_name)
        # Make sure it's a directory and not a file
        if os.path.isdir(app_path):
            # Look for the 'migrations' folder within the app
            migration_dir = os.path.join(app_path, "migrations")

            # Check if 'migrations' directory exists
            if os.path.isdir(migration_dir):
                init_file_path = os.path.join(migration_dir, "__init__.py")

                # If __init__.py does not exist, create it
                if "__init__.py" not in os.listdir(migration_dir):
                    with open(init_file_path, "w"):
                        pass
                    print(f"Created {init_file_path}")

                # Delete all files except __init__.py
                for file in os.listdir(migration_dir):
                    if file != "__init__.py":
                        file_path = os.path.join(migration_dir, file)
                        if os.path.isfile(
                            file_path
                        ):  # Ensure it's a file before deleting
                            os.remove(file_path)
                            print(f"Deleted {file_path}")


if __name__ == "__main__":
    # Specify the path to the 'app' directory
    base_directory = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "app")
    )
    delete_migration_files_except_init(base_directory)
