"""
CSS Manager for loading and managing CSS files individually.
"""
import os
from typing import Dict, Optional, List
from pathlib import Path
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QCoreApplication
from lg import logger

class CSSManager:
    def __init__(self, css_directory: Optional[str] = None):
        self.css_directory = css_directory or "themes/css"
        self.css_cache: Dict[str, str] = {}
        self.applied_styles: List[str] = []
        self._load_all_css_files()
    
    def _load_all_css_files(self):
        try:
            css_path = Path(self.css_directory)
            if not css_path.exists():
                logger.warning(f"CSS directory not found: {css_path}")
                return
            
            for css_file in css_path.glob("*.css"):
                self._load_css_file(css_file)
                
            logger.info(f"CSSManager loaded {len(self.css_cache)} CSS files")
        except Exception as e:
            logger.error(f"Failed to load CSS files: {e}")
    
    def _load_css_file(self, file_path: Path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                filename = file_path.stem
                self.css_cache[filename] = content
        except Exception as e:
            logger.error(f"Failed to load CSS file {file_path}: {e}")
    
    def get_css(self, name: str) -> Optional[str]:
        return self.css_cache.get(name)
    
    def set_css(self, name: str, content: str):
        """Set CSS content for a specific name."""
        self.css_cache[name] = content
        logger.debug(f"Updated CSS content for: {name}")
    
    def reload_css_file(self, name: str) -> bool:
        """Reload a specific CSS file from disk."""
        try:
            css_path = Path(self.css_directory) / f"{name}.css"
            if css_path.exists():
                self._load_css_file(css_path)
                logger.info(f"Reloaded CSS file: {name}")
                return True
            else:
                logger.error(f"CSS file not found for reload: {css_path}")
                return False
        except Exception as e:
            logger.error(f"Failed to reload CSS file {name}: {e}")
            return False
    
    def apply_css(self, name: str, widget=None) -> bool:
        """Apply CSS to application or specific widget."""
        css_content = self.get_css(name)
        if not css_content:
            logger.error(f"CSS not found: {name}")
            return False
        
        try:
            if widget:
                widget.setStyleSheet(css_content)
                logger.info(f"Applied CSS '{name}' to widget: {type(widget).__name__}")
            else:
                app = QApplication.instance()
                if app and isinstance(app, QApplication):
                    app.setStyleSheet(css_content)
                    logger.info(f"Applied CSS '{name}' to application")
                    if name not in self.applied_styles:
                        self.applied_styles.append(name)
                else:
                    logger.error("No QApplication instance found")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to apply CSS '{name}': {e}")
            return False
    
    def combine_css(self, names: List[str]) -> str:
        """Combine multiple CSS files into one string."""
        combined = []
        for name in names:
            css = self.get_css(name)
            if css:
                combined.append(f"/* === CSS: {name} === */")
                combined.append(css)
                combined.append("")
            else:
                logger.warning(f"CSS not found for combining: {name}")
        
        return "\n".join(combined)
    
    def apply_combined_css(self, names: List[str], widget=None) -> bool:
        """Apply multiple CSS files combined."""
        combined_css = self.combine_css(names)
        if not combined_css:
            logger.error("No CSS content to apply")
            return False
        
        try:
            if widget:
                widget.setStyleSheet(combined_css)
                logger.info(f"Applied combined CSS {names} to widget: {type(widget).__name__}")
            else:
                app = QApplication.instance()
                if app and isinstance(app, QApplication):
                    app.setStyleSheet(combined_css)
                    logger.info(f"Applied combined CSS to application: {names}")
                    self.applied_styles = names.copy()
                else:
                    logger.error("No QApplication instance found")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to apply combined CSS {names}: {e}")
            return False
    
    def get_available_themes(self) -> List[str]:
        """Get list of available theme names."""
        return [name for name in self.css_cache.keys() if name.endswith('_theme')]
    
    def has_css(self, name: str) -> bool:
        """Check if CSS exists for given name."""
        return name in self.css_cache
    
    def get_css_info(self) -> Dict[str, int]:
        """Get information about loaded CSS files."""
        return {name: len(content) for name, content in self.css_cache.items()}
