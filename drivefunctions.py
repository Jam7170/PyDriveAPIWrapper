import pydrive, os
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

drive: GoogleDrive
_drive_all_files: list

"""
TODO use threading for non-blocking code
"""

def init_auth():
    global drive
    gauth = GoogleAuth()
    gauth.LocalWebserverAuth()

    drive = GoogleDrive(gauth)

def get_file_list(*, folder=None, trashed=False, _all=False) -> list:
    all_files = drive.ListFile().GetList()
    if _all is True: return all_files
    if trashed is False and folder is None: return all_files

    if trashed is not None and not isinstance(trashed, bool): raise TypeError
    if folder is not None and not isinstance(folder, str): raise TypeError

    folder_id = get_file_id_from_name(folder)
    filtered_files = []

    for file in all_files:
        if trashed is False and file['explicitlyTrashed'] is not False: continue
        if not any(parent['id'] == folder_id for parent in file['parents']): continue

        filtered_files.append(file)

    return filtered_files

def get_file_id_from_name(file_name) -> str | bool:
    """
    Returns the file id for a file with matching name to file_name
    :param file_name: Name of the file in Google Drive
    :return: str | bool
    """
    file_list = get_file_list(_all=True)
    for file in file_list:
        if file_name == file['title']:
            return file['id']
    return False

def upload_file(file_path, *, parent=None, title=None):
    """
    Uploads a local file to Google Drive
    :param str file_path: Path to the file to upload
    :param str parent: Name of a parent folder to upload to
    :param str title: The name to give the file in Google Drive (stays the same by default)
    :return: None
    """
    if not os.path.exists(file_path): raise FileNotFoundError(f"file not found at path: {file_path}")
    if not os.path.isfile(file_path): raise IsADirectoryError("'upload_file' path must be file not directory")
    metadata = {}
    if parent is not None: metadata['parents'] = [{'id': f"{get_file_id_from_name(parent)}"}]
    if title is not None: metadata['title'] = title

    gfile = drive.CreateFile(metadata)
    gfile.SetContentFile(file_path)
    gfile.Upload()

def upload_directory(dir_path, *, parent=None):
    """
    Uploads every file in a directory (not the directory itself) to Google Drive
    :param dir_path: Path of the directory
    :param parent: Name of a parent folder to upload to
    :return: None
    """
    if not os.path.exists(dir_path): raise NotADirectoryError(f"directory not found at path: {dir_path}")
    if os.path.isfile(dir_path): raise NotADirectoryError("'upload_directory' path must be directory not file")
    files = os.listdir(dir_path)
    for file in files:
        upload_file(fr"{dir_path}\{file}", title=file, parent=parent)

def download_file(file_name, *, path='current', name=None, make_dir=False):
    """
    Downloads file from Google Drive that has the given file name
    :param str file_name: Name of the file to download
    :param str path: Path to donwload the file to
    :param str name: Name of the file to write to
    :param bool make_dir: Create the directory if it doesn't exist
    :return: None
    """
    if isinstance(file_name, pydrive.drive.GoogleDriveFile): file_name = file_name['title']
    if name is None: name = file_name
    if path == 'current': path = '.'
    if not os.path.exists(path) and make_dir is True: os.mkdir(path)
    file = drive.CreateFile({'id': get_file_id_from_name(file_name)})
    print(f'Downloading {file["title"]}') #Debug
    file.GetContentFile(f"{path}/{name}")

def download_directory(dir_name, *, path='current', make_dir=False):
    files = get_file_list(folder=dir_name)
    if make_dir is True and not os.path.exists: os.mkdir(path)
    for file in files:
        download_file(file['title'], path=path)