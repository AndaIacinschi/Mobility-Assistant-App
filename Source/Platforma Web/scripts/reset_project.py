import os
import shutil

def delete_file_or_folder(path):
    if os.path.exists(path):
        if os.path.isfile(path):
            os.remove(path)
            print(f"File {path} deleted.")
        elif os.path.isdir(path):
            shutil.rmtree(path)
            print(f"Directory {path} deleted.")
    else:
        print(f"{path} does not exist.")

# Delete the migrations directory
delete_file_or_folder('migrations')

# Delete the SQLite database file
delete_file_or_folder('users.db')

print("Reset complete. You can now reinitialize Alembic and create your tables.")