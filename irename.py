# Rename Images with Date Photo Taken

# Purpose: Renames image files and videos in a folder based on date photo taken from EXIF metadata/the file creation date

# Original Author: Matthew Renze
# Current Implementation: Kamal Sharma

# Behavior:
#  - Given a photo named "Photo Apr 01, 5 54 17 PM.jpg"
#  - with EXIF date taken of "4/1/2018 5:54:17 PM"
#  - when you run this script on its parent folder
#  - then it will be renamed "IMG_20180401_175417.jpg"

# Notes:
#   - For safety, please make a backup of your photos before running this script

# Import libraries
import os
from datetime import datetime
import exifread
from PIL import Image
from pillow_heif import register_heif_opener

register_heif_opener()

# Set list of valid file extensions
valid_image_extensions = [
    ".jpg",
    ".JPG",
    ".jpeg",
    ".JPEG",
    ".png",
    ".PNG",
    ".heic",
    ".HEIC",
]

valid_video_extensions = [".MOV", ".mov", ".MP4", ".mp4", ".MKV", ".mkv"]


class ExifMetadataNotFound(Exception):
    pass


class DateNotFoundInFile(Exception):
    pass


def determine_type(variable):
    return type(variable).__name__


def get_orig_date_from_exifread(file_path: str) -> str:
    # Open image file for reading (must be in binary mode)
    with open(file_path, "rb") as file_handle:
        tags = exifread.process_file(file_handle)

    return str(tags.get("EXIF DateTimeOriginal", ""))


def append_to_file(file_name, content, endl=True):
    file_handle = open(file_name, "a+")
    file_handle.write(content)
    if endl:
        file_handle.write("\n")
    file_handle.close()


def get_file_prefix(file_ext: str) -> str:
    if file_ext in valid_image_extensions:
        return "IMG_"
    elif file_ext in valid_video_extensions:
        return "VID_"
    else:
        return ""


def get_new_file_name(date: datetime, file_extension: str) -> str:
    # Reformat the date taken to "YYYYMMDD-HHmmss"
    # NOTE: Change this line to change the date/time format of the output filename
    date_time = date.strftime("%Y%m%d_%H%M%S")

    # Combine the new file name and file extension
    return get_file_prefix(file_ext) + date_time + file_ext


def get_file_creation_date(file_path: str) -> datetime:
    # File modification timestamp
    m_time = os.path.getmtime(file_path)
    dt_m = datetime.fromtimestamp(m_time)

    # File creation timestamp
    c_time = os.path.getctime(file_path)
    dt_c = datetime.fromtimestamp(c_time)

    # Birth Time
    stat = os.stat(file_path)
    c_timestamp = stat.st_birthtime
    c_time = datetime.fromtimestamp(c_timestamp)

    # Determine the earlier time
    return min(dt_m, dt_c, c_time)


def create_datetime(data) -> datetime:
    return datetime.strptime(data, "%Y:%m:%d %H:%M:%S")


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
        date_taken = create_datetime(metadata[36867])
    elif 306 in metadata.keys():
        date_taken = create_datetime(metadata[306])
    else:
        exifread_dt_sr = get_orig_date_from_exifread(old_file_path)
        if len(exifread_dt_sr) > 0:
            date_taken = create_datetime(exifread_dt_sr)
        else:
            raise DateNotFoundInFile

    # Close the image
    image.close()

    method_1_dt = get_file_creation_date(old_file_path)
    earlier_date = min(method_1_dt, date_taken)

    # Get the date taken as a datetime object
    # date_taken = datetime.strptime(creation_date, "%Y:%m:%d_%H:%M:%S")
    file_ext = os.path.splitext(file_name)[1]
    return get_new_file_name(earlier_date, file_ext)


folder_path = "PhotosCategories/BadmintonDays"
file_names = os.listdir(folder_path)

# For each file
for file_name in file_names:
    # Get the file extension
    file_ext = os.path.splitext(file_name)[1]
    try:
        # Skip files without a valid file extension
        if file_ext in valid_image_extensions:
            new_file_name = get_image_file_name(folder_path, file_name)
        elif file_ext in valid_video_extensions:
            video_file = os.path.join(folder_path, file_name)
            video_creation_date = get_file_creation_date(video_file)
            new_file_name = get_new_file_name(video_creation_date, file_ext)
        else:
            continue

        # Rename the file
        old_file_path = os.path.join(folder_path, file_name)
        new_file_path = os.path.join(folder_path, new_file_name)

        if old_file_path == new_file_path:
            print("Skipping rename! -" + old_file_path)
        else:
            print("Old Name: " + old_file_path)
            print("New Name: " + new_file_path)
            os.rename(old_file_path, new_file_path)
            print("----------------------------")

    except ExifMetadataNotFound:
        append_to_file("meta_not_found.txt", file_name)
        print(f"EXIF metadata not found in file: {file_name}")
    except DateNotFoundInFile:
        append_to_file("date_not_found.txt", file_name)
        print(f"Date not found in file: {file_name}")

        no_data_file = os.path.join(folder_path, file_name)
        file_creation_date = get_file_creation_date(no_data_file)
        new_file_name = get_new_file_name(file_creation_date, file_ext)

        # Rename the file
        old_file_path = os.path.join(folder_path, file_name)
        new_file_path = os.path.join(folder_path, new_file_name)

        if old_file_path == new_file_path:
            print("Skipping rename! -" + old_file_path)
        else:
            print("Old Name: " + old_file_path)
            print("New Name: " + new_file_path)
            os.rename(old_file_path, new_file_path)
            print("----------------------------")
