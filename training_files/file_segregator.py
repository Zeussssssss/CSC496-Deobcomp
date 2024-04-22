import os
import shutil


def segregate_files(directory):
    # Create a dictionary to store file paths based on their types
    file_types = {}

    # Iterate through all files in the directory
    for root, _, files in os.walk(directory):
        for file in files:
            # Extract the type from the filename
            file_name = os.path.splitext(file)[0]
            file_type = file_name.split("_")[1]

            # Create a folder for the type if it doesn't exist
            if file_type not in file_types:
                os.makedirs(os.path.join(directory, file_type))
                file_types[file_type] = []

            # Add the file path to the corresponding type
            file_types[file_type].append(os.path.join(root, file))

    # Move files to their respective folders
    for file_type, files in file_types.items():
        for file_path in files:
            dest_folder = os.path.join(directory, file_type)
            shutil.move(file_path, dest_folder)


if __name__ == "__main__":
    # Directory where the files are extracted
    extract_directory = "progs/img"

    # Call the segregate_files function
    segregate_files(extract_directory)
