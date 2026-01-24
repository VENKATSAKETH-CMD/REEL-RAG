"""
File storage helper.

Implements a small, local disk-based save_upload function used by the upload
endpoint in `app.api.reels`.
"""
import os
import uuid
from pathlib import Path
from fastapi import UploadFile
from typing import Optional

STORAGE_LOCAL_PATH = os.getenv("STORAGE_LOCAL_PATH", "./data/uploads")


async def save_upload(file: UploadFile, dest_filename: Optional[str] = None) -> str:
    """
    Save an UploadFile to disk under STORAGE_LOCAL_PATH.

    Returns the path to the saved file (string) which can be stored as video_url.

    Args:
        file: UploadFile instance from FastAPI
        dest_filename: Optional explicit destination filename. If not provided,
            a random UUID filename will be generated using original extension.

    Returns:
        str: Path to the saved file (relative to the backend working directory)
    """
    Path(STORAGE_LOCAL_PATH).mkdir(parents=True, exist_ok=True)

    if dest_filename:
        filename = dest_filename
    else:
        original = Path(file.filename or "").suffix
        filename = f"{uuid.uuid4().hex}{original}"

    dest_path = Path(STORAGE_LOCAL_PATH) / filename

    # make sure we are at the start of the file
    await file.seek(0)
    contents = await file.read()

    with open(dest_path, "wb") as f:
        f.write(contents)

    # return a path which can be used by the app — use the relative path
    return str(dest_path)
