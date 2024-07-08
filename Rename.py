# Rename Images with Date Photo Taken

# Purpose: Renames image files in a folder based on date photo taken from EXIF metadata

# Author: Matthew Renze

# Behavior:
#  - Given a photo named "Photo Apr 01, 5 54 17 PM.jpg"  
#  - with EXIF date taken of "4/1/2018 5:54:17 PM"  
#  - when you run this script on its parent folder
#  - then it will be renamed "20180401-175417.jpg"

# Notes:
#   - For safety, please make a backup of your photos before running this script

# Import libraries
import os
from datetime import datetime
from PIL import Image

# Set list of valid file extensions
valid_image_extensions = [
    ".jpg", ".JPG",
    ".jpeg", ".JPEG",
    ".png", ".PNG"
]

valid_video_extensions = [
    ".MOV", ".mov",
    ".MP4", ".mp4",
    ".MKV", ".mkv"
]

class ExifMetadataNotFound(Exception):
    pass

class DateNotFoundInFile(Exception):
    pass

def get_new_file_name(date: datetime, file_extension: str) -> str:
    # Reformat the date taken to "YYYYMMDD-HHmmss"
    # NOTE: Change this line to change the date/time format of the output filename
    date_time = date.strftime("%Y%m%d-%H%M%S")
    
    # Combine the new file name and file extension
    return date_time + file_ext

def get_video_creation_date(video_path: str) -> datetime:
    stat = os.stat(video_path)
    c_timestamp = stat.st_birthtime
    c_time = datetime.fromtimestamp(c_timestamp)
    return c_time

def get_image_file_name(folder_path: str, file_name: str) -> str:
    # Create the old file path
    old_file_path = os.path.join(folder_path, file_name)

    # Open the image
    image = Image.open(old_file_path)

    # Get the EXIF metadata
    metadata = image.getexif()

    # Check if the metadata exists
    if metadata is None:
        raise ExifMetadataNotFound

    # Get the date taken from the metadata
    if 36867 in metadata.keys():
        date_taken = metadata[36867]
    elif 306 in metadata.keys():
        date_taken = metadata[306]
    else:
        raise DateNotFoundInFile

    # Close the image
    image.close()

    # Get the date taken as a datetime object
    date_taken = datetime.strptime(date_taken, "%Y:%m:%d %H:%M:%S")
    file_ext = os.path.splitext(file_name)[1]
    return get_new_file_name(date_taken, file_ext)

folder_path = "<Enter Valid Folder Name Here>"

file_names = os.listdir(folder_path)

# For each file
for file_name in file_names:
    # Get the file extension
    file_ext = os.path.splitext(file_name)[1]
    try:
        # Skip files without a valid file extension
        if (file_ext in valid_image_extensions):
            new_file_name = get_image_file_name(folder_path, file_name)
        elif (file_ext in valid_video_extensions):
            video_file = os.path.join(folder_path, file_name)
            video_creation_date = get_video_creation_date(video_file)
            new_file_name = get_new_file_name(video_creation_date, file_ext)
        else:
            continue
        
        # Rename the file
        old_file_path = os.path.join(folder_path, file_name)
        new_file_path = os.path.join(folder_path, new_file_name)
        # print(new_file_path)
        print(old_file_path, new_file_path)
        os.rename(old_file_path, new_file_path)

    except ExifMetadataNotFound:
        print(f"EXIF metadata not found in file: {file_name}")
    except DateNotFoundInFile:
        print(f"Date not found in file: {file_name}")
