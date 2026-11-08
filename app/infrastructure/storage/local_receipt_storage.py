import os
import uuid
from pathlib import Path

from app.domain.storage import ReceiptStorage


class LocalReceiptStorage(ReceiptStorage):
    def __init__(self, directory: str = None):
        self.directory = Path(directory or os.getenv("RECEIPTS_DIR", "uploads/receipts"))
        self.directory.mkdir(parents=True, exist_ok=True)

    def save(self, content: bytes, extension: str) -> str:
        # A random name: the user's file name is never used on disk
        stored_name = f"{uuid.uuid4().hex}{extension}"
        (self.directory / stored_name).write_bytes(content)
        return stored_name

    def delete(self, stored_name: str) -> None:
        (self.directory / Path(stored_name).name).unlink(missing_ok=True)

    def get_path(self, stored_name: str) -> str:
        # Path(...).name strips any folder parts, so no path tricks are possible
        return str(self.directory / Path(stored_name).name)