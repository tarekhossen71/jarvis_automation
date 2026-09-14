import os
import shutil
import subprocess
import ctypes
from pathlib import Path
from datetime import datetime

from send2trash import send2trash


# =========================================================
# PENDING CONFIRMATION STATE
# =========================================================

_pending_action = None


# =========================================================
# PATH HELPERS
# =========================================================

def resolve_path(path: str = ""):
    """
    Resolve common Windows folders and paths.
    """

    home = Path.home()

    aliases = {
        "home": home,
        "desktop": home / "Desktop",
        "downloads": home / "Downloads",
        "documents": home / "Documents",
        "pictures": home / "Pictures",
        "music": home / "Music",
        "videos": home / "Videos",
    }

    path = (path or "").strip()

    if not path:
        return home

    key = path.lower()

    if key in aliases:
        return aliases[key].resolve()

    expanded = os.path.expandvars(
        os.path.expanduser(path)
    )

    path_obj = Path(expanded)

    if path_obj.is_absolute():
        return path_obj.resolve()

    return Path.cwd().joinpath(path_obj).resolve()


# =========================================================
# LIST FOLDER
# =========================================================

def list_folder(path: str = ""):
    """
    List files and folders inside a directory.
    """

    try:
        folder = resolve_path(path)

        if not folder.exists():
            return {
                "success": False,
                "error": f"Folder does not exist: {folder}",
            }

        if not folder.is_dir():
            return {
                "success": False,
                "error": f"Not a folder: {folder}",
            }

        folders = []
        files = []

        for item in folder.iterdir():
            try:
                if item.is_dir():
                    folders.append(item.name)
                else:
                    files.append(item.name)
            except PermissionError:
                continue

        folders = sorted(folders)[:50]
        files = sorted(files)[:50]

        return {
            "success": True,
            "path": str(folder),
            "folder_count": len(folders),
            "file_count": len(files),
            "folders": folders,
            "files": files,
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }


# =========================================================
# SEARCH FILES
# =========================================================

def search_files(name: str, path: str = ""):
    """
    Search for files or folders by name.
    """

    try:
        name = (name or "").strip()

        if not name:
            return {
                "success": False,
                "error": "Search name cannot be empty.",
            }

        root = resolve_path(path)

        if not root.exists():
            return {
                "success": False,
                "error": f"Search folder does not exist: {root}",
            }

        if not root.is_dir():
            return {
                "success": False,
                "error": f"Search path is not a folder: {root}",
            }

        results = []
        search_name = name.lower()

        ignored_dirs = {
            "__pycache__",
            ".git",
            ".venv",
            "venv",
            "node_modules",
        }

        for current_root, dirs, files in os.walk(root):

            dirs[:] = [
                d for d in dirs
                if d.lower() not in ignored_dirs
            ]

            for filename in files:
                if search_name in filename.lower():
                    results.append(
                        str(Path(current_root) / filename)
                    )

                    if len(results) >= 20:
                        break

            if len(results) >= 20:
                break

            for dirname in dirs:
                if search_name in dirname.lower():
                    results.append(
                        str(Path(current_root) / dirname)
                    )

                    if len(results) >= 20:
                        break

            if len(results) >= 20:
                break

        return {
            "success": True,
            "search": name,
            "root": str(root),
            "result_count": len(results),
            "results": results,
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }


# =========================================================
# FILE / FOLDER INFORMATION
# =========================================================

def get_file_info(path: str):
    """
    Get information about a file or folder.
    """

    try:
        target = resolve_path(path)

        if not target.exists():
            return {
                "success": False,
                "error": f"File or folder does not exist: {target}",
            }

        stat = target.stat()

        if target.is_file():

            size_bytes = stat.st_size

            if size_bytes < 1024:
                size = f"{size_bytes} B"
            elif size_bytes < 1024 ** 2:
                size = f"{round(size_bytes / 1024, 2)} KB"
            elif size_bytes < 1024 ** 3:
                size = f"{round(size_bytes / (1024 ** 2), 2)} MB"
            else:
                size = f"{round(size_bytes / (1024 ** 3), 2)} GB"

            item_type = "file"

        else:
            size = None
            item_type = "folder"

        modified = datetime.fromtimestamp(
            stat.st_mtime
        ).strftime("%Y-%m-%d %H:%M:%S")

        return {
            "success": True,
            "name": target.name,
            "path": str(target),
            "type": item_type,
            "size": size,
            "modified": modified,
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }


# =========================================================
# CREATE FILE
# =========================================================

def create_file(path: str, content: str = ""):
    """
    Create a new text file.
    Existing files are never overwritten.
    """

    try:
        target = resolve_path(path)

        if target.exists():
            return {
                "success": False,
                "error": f"File already exists: {target}",
            }

        if not target.parent.exists():
            return {
                "success": False,
                "error": (
                    f"Parent folder does not exist: "
                    f"{target.parent}"
                ),
            }

        target.write_text(
            content or "",
            encoding="utf-8"
        )

        return {
            "success": True,
            "path": str(target),
            "message": (
                f"File created successfully: "
                f"{target.name}"
            ),
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }


# =========================================================
# CREATE FOLDER
# =========================================================

def create_folder(path: str):
    """
    Create a new folder.
    """

    try:
        target = resolve_path(path)

        if target.exists():
            return {
                "success": False,
                "error": f"File or folder already exists: {target}",
            }

        target.mkdir(
            parents=False,
            exist_ok=False
        )

        return {
            "success": True,
            "path": str(target),
            "message": (
                f"Folder created successfully: "
                f"{target.name}"
            ),
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }


# =========================================================
# RENAME
# =========================================================

def rename_file(path: str, new_name: str):
    """
    Rename a file or folder.
    """

    try:
        target = resolve_path(path)
        new_name = (new_name or "").strip()

        if not target.exists():
            return {
                "success": False,
                "error": f"File or folder does not exist: {target}",
            }

        if not new_name:
            return {
                "success": False,
                "error": "New name cannot be empty.",
            }

        if Path(new_name).name != new_name:
            return {
                "success": False,
                "error": (
                    "New name must contain only "
                    "a file or folder name."
                ),
            }

        destination = target.parent / new_name

        if destination.exists():
            return {
                "success": False,
                "error": (
                    f"Destination already exists: "
                    f"{destination}"
                ),
            }

        target.rename(destination)

        return {
            "success": True,
            "old_path": str(target),
            "new_path": str(destination),
            "message": f"Renamed to {new_name}.",
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }


# =========================================================
# COPY
# =========================================================

def copy_file(source: str, destination: str):
    """
    Copy a file or folder into an existing destination folder.
    Existing destination items are not overwritten.
    """

    try:
        source_path = resolve_path(source)
        destination_folder = resolve_path(destination)

        if not source_path.exists():
            return {
                "success": False,
                "error": f"Source does not exist: {source_path}",
            }

        if not destination_folder.exists():
            return {
                "success": False,
                "error": (
                    f"Destination folder does not exist: "
                    f"{destination_folder}"
                ),
            }

        if not destination_folder.is_dir():
            return {
                "success": False,
                "error": (
                    f"Destination is not a folder: "
                    f"{destination_folder}"
                ),
            }

        destination_path = (
            destination_folder / source_path.name
        )

        if destination_path.exists():
            return {
                "success": False,
                "error": (
                    f"Destination already contains: "
                    f"{source_path.name}"
                ),
            }

        if source_path.is_dir():
            shutil.copytree(
                str(source_path),
                str(destination_path)
            )
        else:
            shutil.copy2(
                str(source_path),
                str(destination_path)
            )

        return {
            "success": True,
            "source": str(source_path),
            "destination": str(destination_path),
            "message": (
                f"Copied {source_path.name} successfully."
            ),
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }


# =========================================================
# MOVE
# =========================================================

def move_file(source: str, destination: str):
    """
    Move a file or folder into an existing destination folder.
    Existing destination items are not overwritten.
    """

    try:
        source_path = resolve_path(source)
        destination_folder = resolve_path(destination)

        if not source_path.exists():
            return {
                "success": False,
                "error": f"Source does not exist: {source_path}",
            }

        if not destination_folder.exists():
            return {
                "success": False,
                "error": (
                    f"Destination folder does not exist: "
                    f"{destination_folder}"
                ),
            }

        if not destination_folder.is_dir():
            return {
                "success": False,
                "error": (
                    f"Destination is not a folder: "
                    f"{destination_folder}"
                ),
            }

        destination_path = (
            destination_folder / source_path.name
        )

        if destination_path.exists():
            return {
                "success": False,
                "error": (
                    f"Destination already contains: "
                    f"{source_path.name}"
                ),
            }

        shutil.move(
            str(source_path),
            str(destination_path)
        )

        return {
            "success": True,
            "old_path": str(source_path),
            "new_path": str(destination_path),
            "message": (
                f"Moved {source_path.name} successfully."
            ),
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }


# =========================================================
# OPEN FILE
# =========================================================

def open_file(path: str):
    """
    Open a file using the Windows default application.
    """

    try:
        target = resolve_path(path)

        if not target.exists():
            return {
                "success": False,
                "error": f"File does not exist: {target}",
            }

        if not target.is_file():
            return {
                "success": False,
                "error": f"Not a file: {target}",
            }

        os.startfile(str(target))

        return {
            "success": True,
            "path": str(target),
            "message": f"Opened {target.name}.",
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }


# =========================================================
# OPEN FOLDER
# =========================================================

def open_folder(path: str):
    """
    Open a folder in Windows File Explorer.
    """

    try:
        folder = resolve_path(path)

        if not folder.exists():
            return {
                "success": False,
                "error": f"Folder does not exist: {folder}",
            }

        if not folder.is_dir():
            return {
                "success": False,
                "error": f"Not a folder: {folder}",
            }

        os.startfile(str(folder))

        return {
            "success": True,
            "path": str(folder),
            "message": f"Opened folder {folder.name}.",
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }


# =========================================================
# RECENT FILES
# =========================================================

def get_recent_files(path: str = "", limit: int = 10):
    """
    Get recently modified files from a folder.
    """

    try:
        root = resolve_path(path)

        if not root.exists():
            return {
                "success": False,
                "error": f"Folder does not exist: {root}",
            }

        if not root.is_dir():
            return {
                "success": False,
                "error": f"Not a folder: {root}",
            }

        files = []

        ignored_dirs = {
            "__pycache__",
            ".git",
            ".venv",
            "venv",
            "node_modules",
        }

        for current_root, dirs, filenames in os.walk(root):

            dirs[:] = [
                d for d in dirs
                if d.lower() not in ignored_dirs
            ]

            for filename in filenames:
                try:
                    filepath = Path(current_root) / filename
                    modified = filepath.stat().st_mtime

                    files.append(
                        {
                            "name": filename,
                            "path": str(filepath),
                            "modified_timestamp": modified,
                        }
                    )

                except (PermissionError, FileNotFoundError):
                    continue

        files.sort(
            key=lambda item: item["modified_timestamp"],
            reverse=True
        )

        results = []

        for item in files[:max(1, min(int(limit), 30))]:
            results.append(
                {
                    "name": item["name"],
                    "path": item["path"],
                    "modified": datetime.fromtimestamp(
                        item["modified_timestamp"]
                    ).strftime("%Y-%m-%d %H:%M:%S"),
                }
            )

        return {
            "success": True,
            "root": str(root),
            "count": len(results),
            "files": results,
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }


# =========================================================
# DELETE REQUEST
# =========================================================

def delete_file(path: str):
    """
    Request deletion of a file or folder.

    This NEVER deletes immediately.
    It creates a pending confirmation request.
    """

    global _pending_action

    try:
        target = resolve_path(path)

        if not target.exists():
            return {
                "success": False,
                "error": (
                    f"File or folder does not exist: "
                    f"{target}"
                ),
            }

        item_type = (
            "folder"
            if target.is_dir()
            else "file"
        )

        _pending_action = {
            "type": "delete",
            "path": str(target),
        }

        return {
            "success": True,
            "requires_confirmation": True,
            "name": target.name,
            "path": str(target),
            "type": item_type,
            "message": (
                f"Confirmation required before moving "
                f"{item_type} '{target.name}' "
                f"to the Recycle Bin."
            ),
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }


# =========================================================
# CONFIRM DELETE
# =========================================================

def confirm_delete():
    """
    Confirm the pending delete request.

    Only operates on the internally stored pending item.
    """

    global _pending_action

    try:
        if not _pending_action:
            return {
                "success": False,
                "error": "There is no pending delete request.",
            }

        if _pending_action["type"] != "delete":
            return {
                "success": False,
                "error": "Pending action is not a delete request.",
            }

        target = Path(
            _pending_action["path"]
        )

        if not target.exists():
            _pending_action = None

            return {
                "success": False,
                "error": (
                    "The pending file or folder "
                    "no longer exists."
                ),
            }

        name = target.name

        send2trash(str(target))

        _pending_action = None

        return {
            "success": True,
            "message": (
                f"{name} was moved to the "
                f"Windows Recycle Bin."
            ),
        }

    except Exception as e:
        _pending_action = None

        return {
            "success": False,
            "error": str(e),
        }


# =========================================================
# CANCEL DELETE
# =========================================================

def cancel_delete():
    """
    Cancel the pending delete request.
    """

    global _pending_action

    if not _pending_action:
        return {
            "success": True,
            "message": "There is no pending delete request.",
        }

    name = Path(
        _pending_action["path"]
    ).name

    _pending_action = None

    return {
        "success": True,
        "message": (
            f"Delete cancelled. "
            f"{name} was not deleted."
        ),
    }


# =========================================================
# EMPTY RECYCLE BIN REQUEST
# =========================================================

def empty_recycle_bin():
    """
    Request emptying the Windows Recycle Bin.

    This NEVER empties immediately.
    It creates a pending confirmation request.
    """

    global _pending_action

    _pending_action = {
        "type": "empty_recycle_bin",
    }

    return {
        "success": True,
        "requires_confirmation": True,
        "message": (
            "Confirmation required. "
            "Emptying the Recycle Bin permanently "
            "deletes all items and cannot be undone."
        ),
    }


# =========================================================
# CONFIRM EMPTY RECYCLE BIN
# =========================================================

def confirm_empty_recycle_bin():
    """
    Permanently empty the Windows Recycle Bin.
    Only works after an explicit pending confirmation.
    """

    global _pending_action

    try:
        if not _pending_action:
            return {
                "success": False,
                "error": (
                    "There is no pending "
                    "Recycle Bin confirmation."
                ),
            }

        if _pending_action["type"] != "empty_recycle_bin":
            return {
                "success": False,
                "error": (
                    "Pending action is not "
                    "Recycle Bin emptying."
                ),
            }

        # Windows SHEmptyRecycleBin flags
        # 0x01 = no confirmation
        # 0x02 = no progress UI
        # 0x04 = no sound
        flags = 0x01 | 0x02 | 0x04

        result = ctypes.windll.shell32.SHEmptyRecycleBinW(
            None,
            None,
            flags
        )

        _pending_action = None

        if result != 0:
            return {
                "success": False,
                "error": (
                    f"Windows could not empty "
                    f"the Recycle Bin. Error code: {result}"
                ),
            }

        return {
            "success": True,
            "message": (
                "Recycle Bin emptied successfully. "
                "All items were permanently deleted."
            ),
        }

    except Exception as e:
        _pending_action = None

        return {
            "success": False,
            "error": str(e),
        }


# =========================================================
# CANCEL RECYCLE BIN EMPTY
# =========================================================

def cancel_recycle_bin():
    """
    Cancel the pending Recycle Bin empty request.
    """

    global _pending_action

    if (
        _pending_action
        and _pending_action["type"] == "empty_recycle_bin"
    ):
        _pending_action = None

        return {
            "success": True,
            "message": "Recycle Bin emptying cancelled.",
        }

    return {
        "success": True,
        "message": "There is no pending Recycle Bin action.",
    }