from abc import ABC, abstractmethod


class ReceiptStorage(ABC):
    """Where uploaded receipt images are kept. The domain does not care
    whether this is a local folder or cloud storage."""

    @abstractmethod
    def save(self, content: bytes, extension: str) -> str:
        """Stores the file and returns the stored file name."""

    @abstractmethod
    def delete(self, stored_name: str) -> None: ...

    @abstractmethod
    def get_path(self, stored_name: str) -> str: ...