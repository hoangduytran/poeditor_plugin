    def _cut_items(self, paths: List[str]):
        """Cut selected items to clipboard."""
        try:
            # Create mime data
            mime_data = self._create_file_mime_data(paths)
            
            # Set operation type for paste
            mime_data.setData("application/x-explorer-operation", b"cut")
            
            # Set clipboard data
            clipboard = QApplication.clipboard()
            clipboard.setMimeData(mime_data)
            
            logger.debug(f"Cut items to clipboard: {paths}")
        except Exception as e:
            logger.error(f"Error cutting items: {e}")
            
    def _copy_items(self, paths: List[str]):
        """Copy selected items to clipboard."""
        try:
            # Create mime data
            mime_data = self._create_file_mime_data(paths)
            
            # Set operation type for paste
            mime_data.setData("application/x-explorer-operation", b"copy")
            
            # Set clipboard data
            clipboard = QApplication.clipboard()
            clipboard.setMimeData(mime_data)
            
            logger.debug(f"Copied items to clipboard: {paths}")
        except Exception as e:
            logger.error(f"Error copying items: {e}")
            
    def _paste_items(self, target_path: str):
        """Paste items from clipboard to target path."""
        try:
            # Get clipboard data
            clipboard = QApplication.clipboard()
            mime_data = clipboard.mimeData()
            
            if not self._clipboard_has_files(mime_data):
                logger.warning("Clipboard does not contain files")
                return
            
            # Get paths from clipboard
            paths = self._get_paths_from_mime_data(mime_data)
            
            # Get operation type (cut or copy)
            operation_bytes = mime_data.data("application/x-explorer-operation")
            operation = operation_bytes.data().decode('utf-8') if operation_bytes else "copy"
            
            # Perform operation
            if operation == "cut":
                self.file_operations_service.move_items(paths, target_path)
            else:  # copy
                self.file_operations_service.copy_items(paths, target_path)
                
            logger.debug(f"Pasted items to {target_path}: {paths}")
        except Exception as e:
            logger.error(f"Error pasting items: {e}")
            
    def _delete_items(self, paths: List[str]):
        """Delete selected items."""
        try:
            # Confirm deletion
            confirm = QMessageBox.question(
                None,  # Parent window
                "Confirm Delete",
                f"Are you sure you want to delete {len(paths)} item(s)?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if confirm == QMessageBox.StandardButton.Yes:
                # Delete items
                self.file_operations_service.delete_items(paths)
                logger.debug(f"Deleted items: {paths}")
        except Exception as e:
            logger.error(f"Error deleting items: {e}")
            
    def _rename_item(self, path: str):
        """Rename selected item."""
        try:
            # Get current name
            current_name = os.path.basename(path)
            
            # Show dialog to get new name
            new_name, ok = QInputDialog.getText(
                None,  # Parent window
                "Rename",
                "Enter new name:",
                text=current_name
            )
            
            if ok and new_name:
                # Rename item
                new_path = os.path.join(os.path.dirname(path), new_name)
                self.file_operations_service.rename_item(path, new_path)
                logger.debug(f"Renamed {path} to {new_path}")
        except Exception as e:
            logger.error(f"Error renaming item: {e}")
            
    def _create_new_file(self, directory: str):
        """Create a new file in the specified directory."""
        try:
            # Show dialog to get file name
            file_name, ok = QInputDialog.getText(
                None,  # Parent window
                "New File",
                "Enter file name:",
            )
            
            if ok and file_name:
                # Create file
                file_path = os.path.join(directory, file_name)
                self.file_operations_service.create_file(file_path)
                logger.debug(f"Created new file: {file_path}")
        except Exception as e:
            logger.error(f"Error creating new file: {e}")
            
    def _create_new_folder(self, directory: str):
        """Create a new folder in the specified directory."""
        try:
            # Show dialog to get folder name
            folder_name, ok = QInputDialog.getText(
                None,  # Parent window
                "New Folder",
                "Enter folder name:",
            )
            
            if ok and folder_name:
                # Create folder
                folder_path = os.path.join(directory, folder_name)
                self.file_operations_service.create_folder(folder_path)
                logger.debug(f"Created new folder: {folder_path}")
        except Exception as e:
            logger.error(f"Error creating new folder: {e}")
            
    def _clipboard_has_files(self, mime_data: QMimeData) -> bool:
        """Check if clipboard has file data."""
        return mime_data.hasFormat("application/x-explorer-file-list")
    
    def _create_file_mime_data(self, paths: List[str]) -> QMimeData:
        """Create mime data for file operations."""
        mime_data = QMimeData()
        
        # Store paths as text
        mime_data.setText("\n".join(paths))
        
        # Store paths in custom format for internal operations
        path_bytes = "\n".join(paths).encode('utf-8')
        mime_data.setData("application/x-explorer-file-list", path_bytes)
        
        # Create URLs for system-wide drag and drop
        urls = [QUrl.fromLocalFile(path) for path in paths]
        mime_data.setUrls(urls)
        
        return mime_data
    
    def _get_paths_from_mime_data(self, mime_data: QMimeData) -> List[str]:
        """Get file paths from mime data."""
        if mime_data.hasFormat("application/x-explorer-file-list"):
            # Get paths from custom format
            path_bytes = mime_data.data("application/x-explorer-file-list")
            paths_str = path_bytes.data().decode('utf-8')
            return paths_str.split("\n")
        elif mime_data.hasUrls():
            # Get paths from URLs
            urls = mime_data.urls()
            return [url.toLocalFile() for url in urls if url.isLocalFile()]
        elif mime_data.hasText():
            # Get paths from text
            return mime_data.text().split("\n")
        
        return []
        
    def _open_items(self, paths: List[str]):
        """Open selected items."""
        for path in paths:
            try:
                if os.path.isfile(path):
                    # Open file
                    if platform.system() == "Windows":
                        os.startfile(path)
                    elif platform.system() == "Darwin":  # macOS
                        subprocess.call(["open", path])
                    else:  # Linux
                        subprocess.call(["xdg-open", path])
                elif os.path.isdir(path):
                    # Open directory in file explorer
                    self.file_operations_service.open_directory(path)
            except Exception as e:
                logger.error(f"Error opening item {path}: {e}")
                
    def _open_in_new_window(self, paths: List[str]):
        """Open directories in new window."""
        for path in paths:
            try:
                if os.path.isdir(path):
                    # This should be implemented based on application design
                    # For example, by emitting a signal to open a new window
                    logger.debug(f"Opening directory in new window: {path}")
                    # self.open_in_new_window_signal.emit(path)
            except Exception as e:
                logger.error(f"Error opening directory in new window {path}: {e}")
