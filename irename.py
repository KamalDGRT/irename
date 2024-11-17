# Rename Images with Date Photo Taken

# Purpose: Renames image files and videos in a folder based on date photo taken from EXIF metadata/the file creation date

# Original Author: Matthew Renze
# Current Implementation: Kamal Sharma
# With slight tweaks from ChatGPT

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
from PIL import Image, UnidentifiedImageError
from pillow_heif import register_heif_opener

register_heif_opener()

# Set valid file extensions
VALID_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".heic"}
VALID_VIDEO_EXTENSIONS = {".mov", ".mp4", ".mkv"}
VALID_EXTENSIONS = VALID_IMAGE_EXTENSIONS | VALID_VIDEO_EXTENSIONS


class ExifMetadataNotFound(Exception):
    pass


class DateNotFoundInFile(Exception):
    pass


def append_to_file(file_name: str, content: str, endl: bool = True):
    """Append content to a file."""
    with open(file_name, "a+") as file_handle:
        file_handle.write(content)
        if endl:
            file_handle.write("\n")


def get_file_prefix(file_ext: str) -> str:
    """Get file prefix based on file type."""
    if file_ext in VALID_IMAGE_EXTENSIONS:
        return "IMG_"
    elif file_ext in VALID_VIDEO_EXTENSIONS:
        return "VID_"
    return ""


def get_new_file_name(date: datetime, file_extension: str) -> str:
    """Generate a new file name based on the date."""
    date_time = date.strftime("%Y%m%d_%H%M%S")
    return f"{get_file_prefix(file_extension)}{date_time}{file_extension}"


def get_file_creation_date(file_path: str) -> datetime:
    """Get the earliest date between creation, modification, and birth time."""
    stats = os.stat(file_path)
    m_time = datetime.fromtimestamp(stats.st_mtime)
    c_time = datetime.fromtimestamp(stats.st_ctime)
    b_time = datetime.fromtimestamp(getattr(stats, "st_birthtime", stats.st_ctime))
    return min(m_time, c_time, b_time)


def create_datetime(date_str: str) -> datetime:
    """Convert a date string into a datetime object."""
    return datetime.strptime(date_str, "%Y:%m:%d %H:%M:%S")


def get_exif_date(file_path: str) -> datetime:
    """Retrieve the EXIF date or fallback to file creation date."""
    try:
        with Image.open(file_path) as image:
            metadata = image.getexif()
            if 36867 in metadata:  # DateTimeOriginal
                return create_datetime(metadata[36867])
            elif 306 in metadata:  # DateTime
                return create_datetime(metadata[306])
    except (KeyError, ValueError):
        pass

    # Fallback to exifread library
    with open(file_path, "rb") as file_handle:
        tags = exifread.process_file(file_handle)
    exif_date = tags.get("EXIF DateTimeOriginal")
    if exif_date:
        return create_datetime(str(exif_date))

    raise ExifMetadataNotFound


def process_file(file_path: str, file_extension: str) -> str:
    """Process a file and generate a new name based on metadata or creation date."""
    try:
        date = get_exif_date(file_path)
    except ExifMetadataNotFound:
        append_to_file("meta_not_found.txt", os.path.basename(file_path))
        date = get_file_creation_date(file_path)
    except DateNotFoundInFile:
        append_to_file("date_not_found.txt", os.path.basename(file_path))
        date = get_file_creation_date(file_path)

    return get_new_file_name(date, file_extension)


def rename_file(folder_path: str, file_name: str):
    """Rename a file based on metadata or creation date."""
    file_path = os.path.join(folder_path, file_name)
    file_extension = os.path.splitext(file_name)[1].lower()

    if file_extension not in VALID_EXTENSIONS:
        return

    try:
        if file_extension in VALID_IMAGE_EXTENSIONS:
            new_name = process_file(file_path, file_extension)
        elif file_extension in VALID_VIDEO_EXTENSIONS:
            video_date = get_file_creation_date(file_path)
            new_name = get_new_file_name(video_date, file_extension)
        
        new_path = os.path.join(folder_path, new_name)

        if file_path == new_path:
            print(f"Skipping rename! - {file_path}")
        else:
            print(f"Old Name: {file_path}")
            print(f"New Name: {new_path}")
            os.rename(file_path, new_path)
            print("----------------------------")
    except UnidentifiedImageError:
        append_to_file("invalid_image_files.txt", file_name)
        print(f"Unidentified image file: {file_name}")


def main(folder_path: str):
    """Main function to process files in a folder."""
    for file_name in os.listdir(folder_path):
        rename_file(folder_path, file_name)


# Run the script
if __name__ == "__main__":
    folder_path = "/user/xyz/down/up"
    main(folder_path)
