import os

def rename_files(folder_path, old_substring, new_substring):
    """
    Rename files in a folder by replacing a substring in their names
    Args:
        folder_path (str): Path to the folder containing files
        Old_substring (str): Substring to find in the filenames
        new_substring (str): Substring to replace with

    """

    # Verify folder exists
    if not os.path.isdir(folder_path):
        print(f"Error: Folder {folder_path} does not exist")
        return
    
    # Get all the files in the folder
    files = [file_ for file_ in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, file_))]

    renamed_count = 0

    for filename in files:
        if old_substring in filename:
            # Create new filename
            new_filename = filename.replace(old_substring, new_substring)

            # Get full paths
            old_path = os.path.join(folder_path, filename)
            new_path = os.path.join(folder_path, new_filename)

            # Rename the file
            os.rename(old_path, new_path)
            print(f"Renamed: {filename} -> {new_filename}")
            renamed_count += 1

    print(f"\nDone! {renamed_count} files renamed.")

if __name__ == "__main__":
    # Example usage
    folder_path = "/home/newtonjeri2204/ros2_work_ws/Hyperspawn-Dropbear/src/Hyperspawn-Dropbear-Humanoid/hyperspawn_dropbear_description/meshes/left_arm"
    old_substring = "Mirror___1__"
    # old_substring = "Mirror___2__"
    new_substring = ""

    rename_files(folder_path, old_substring, new_substring)