"""
ciobrain/admin/documents/documents_manager.py

Classes:
    - DocumentsManager: manages documents operations
    - StorageHandler: used by DocumentsManager to handle file operations
"""

import os
from flask import current_app
from werkzeug.utils import secure_filename

class DocumentsManager:
    """Manages document actions such as upload, obfuscation, and review"""

    def __init__(self):
        self.active_document = None
        self.storage_handler = StorageHandler()

    def get_directories(self) -> dict[str, list[str]]:
        """Get directory contents using the StorageHandler"""
        return self.storage_handler.get_directory_contents()

    def upload_document(self, file) -> str:
        """Handle document upload using StorageHandler"""
        return self.storage_handler.process_upload(file)

    def obfuscate_document(self):
        """Placeholder for obfuscation logic."""
        if not self.active_document:
            raise ValueError("No document selected")

    def review_document(self):
        """Placeholder for review logic."""
        if not self.active_document:
            raise ValueError("No document available for review")

class StorageHandler:
    """Handles validation and file operations"""

    def get_directory_contents(self) -> dict[str, list[str]]:
        """Retrieve the contents of the storage directories."""
        directories = {
            'uploads': os.listdir(current_app.config['UPLOADS']),
            'working': os.listdir(current_app.config['WORKING']),
            'reviewed': os.listdir(current_app.config['REVIEWED']),
        }
        return directories

    def process_upload(self, file) -> str:
        """validate and save a file in one call. """
        self._validate_file(file)
        return self._save_file(file)

    def _validate_file(self, file) -> None:
        """Validate the file extension based on allowed extensions."""
        allowed_extensions = self._get_allowed_extensions()
        file_extension = os.path.splitext(file.filename)[1].lower()
        if '.' not in file.filename or file_extension not in allowed_extensions:
            raise ValueError("Unsuported file type")

    def _save_file(self, file) -> str:
        """Save validated file to uploads directory."""
        uploads_directory = current_app.config['UPLOADS']
        filename = secure_filename(file.filename)
        file_path = os.path.join(uploads_directory, filename)
        file.save(file_path)
        return file_path

    def _get_allowed_extensions(self) -> set[str]:
        """Retrieve allowed extensions from config."""
        allowed_extensions = current_app.config.get('ALLOWED_EXTENSIONS')
        if not allowed_extensions:
            raise ValueError("ALLOWED_EXTENSIONS is not configured")
        return allowed_extensions
