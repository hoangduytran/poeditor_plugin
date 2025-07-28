    # Shortcut handler methods
    def _shortcut_cut(self):
        """Handle cut shortcut."""
        self._handle_selection_shortcut('cut')
    
    def _shortcut_copy(self):
        """Handle copy shortcut."""
        self._handle_selection_shortcut('copy')
    
    def _shortcut_paste(self):
        """Handle paste shortcut."""
        # Only works if we have a current directory
        if self.current_directory:
            self._paste_items(self.current_directory)
    
    def _shortcut_delete(self):
        """Handle delete shortcut."""
        self._handle_selection_shortcut('delete')
    
    def _shortcut_rename(self):
        """Handle rename shortcut."""
        self._handle_selection_shortcut('rename')
    
    def _shortcut_new_file(self):
        """Handle new file shortcut."""
        if self.current_directory:
            self._create_new_file(self.current_directory)
    
    def _shortcut_new_folder(self):
        """Handle new folder shortcut."""
        if self.current_directory:
            self._create_new_folder(self.current_directory)
    
    def _shortcut_refresh(self):
        """Handle refresh shortcut."""
        self.refresh_requested.emit()
    
    def _handle_selection_shortcut(self, operation: str):
        """
        Handle shortcuts for operations that require selected items.
        
        This is called by the individual shortcut handlers when
        we need to apply an operation to currently selected items.
        
        The Explorer panel should update this object's 'selected_items'
        property whenever selection changes.
        
        Args:
            operation: The operation to perform ('cut', 'copy', 'delete', 'rename')
        """
        # This requires the Explorer panel to set this property when selection changes
        if not hasattr(self, 'selected_items') or not self.selected_items:
            logger.debug(f"No items selected for {operation} shortcut")
            return
        
        items = self.selected_items
        paths = [item['path'] for item in items]
        
        if operation == 'cut':
            self._cut_items(paths)
        elif operation == 'copy':
            self._copy_items(paths)
        elif operation == 'delete':
            self._delete_items(paths)
        elif operation == 'rename' and len(items) == 1:
            self._rename_item(items[0]['path'])
