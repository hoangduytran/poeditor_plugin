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
        self.styles_directory = "styles"
        self.current_css_file = os.path.join(self.css_directory, "light_theme.css") # default
        self.css_cache: Dict[str, str] = {}
        self.applied_styles: List[str] = []
        self._load_all_css_files()
        self._load_style_files()
    
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
                self.current_css_file = str(file_path)  # Keep full path for debugging
            logger.info(f"Loaded CSS file: {self.current_css_file} ({len(content)} chars)")
        except Exception as e:
            logger.error(f"Failed to load CSS file {file_path}: {e}")
    
    def get_css(self, name: str) -> Optional[str]:
        return self.css_cache.get(name)
    
    def set_css(self, name: str, content: str):
        """Set CSS content for a specific name."""
        self.css_cache[name] = content
        logger.debug(f"Updated CSS content for: {name}")
    
    def _load_style_files(self):
        """Load CSS files from the styles directory."""
        try:
            styles_path = Path(self.styles_directory)
            if not styles_path.exists():
                logger.warning(f"Styles directory not found: {styles_path}")
                return
            
            # Load specific style files
            style_files = ["context_menu.css", "common.css"]
            for style_file in style_files:
                file_path = styles_path / style_file
                if file_path.exists():
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            filename = file_path.stem
                            self.css_cache[filename] = content
                        logger.info(f"Loaded style file: {file_path} ({len(content)} chars)")
                    except Exception as e:
                        logger.error(f"Failed to load style file {file_path}: {e}")
                        
            logger.info(f"CSSManager loaded styles from {self.styles_directory}")
        except Exception as e:
            logger.error(f"Failed to load style files: {e}")
    
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
        
        # Update current CSS file path for debugging
        css_file_path = os.path.join(self.css_directory, f"{name}.css")
        self.current_css_file = css_file_path
        
        try:
            if widget:
                widget.setStyleSheet(css_content)
                logger.info(f"Applied CSS '{name}' to widget: {type(widget).__name__} (from: {self.current_css_file})")
                # Update applied styles for widget applications too
                if name not in self.applied_styles:
                    self.applied_styles.append(name)
            else:
                app = QApplication.instance()
                if app and isinstance(app, QApplication):
                    app.setStyleSheet(css_content)
                    logger.info(f"Applied CSS '{name}' to application (from: {self.current_css_file})")
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
        
        # Update current CSS file info for debugging (combined files)
        combined_files = [os.path.join(self.css_directory, f"{name}.css") for name in names]
        self.current_css_file = f"Combined: {', '.join(combined_files)}"
        
        try:
            if widget:
                widget.setStyleSheet(combined_css)
                logger.info(f"Applied combined CSS {names} to widget: {type(widget).__name__} (from: {self.current_css_file})")
                # Update applied styles for widget applications too
                self.applied_styles = names.copy()
            else:
                app = QApplication.instance()
                if app and isinstance(app, QApplication):
                    app.setStyleSheet(combined_css)
                    logger.info(f"Applied combined CSS to application: {names} (from: {self.current_css_file})")
                    self.applied_styles = names.copy()
                else:
                    logger.error("No QApplication instance found")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to apply combined CSS {names}: {e}")
            return False
    
    def get_available_themes(self) -> List[str]:
        """Get list of available theme names by discovering CSS files in theme directory."""
        themes = []
        
        try:
            css_path = Path(self.css_directory)
            if not css_path.exists():
                logger.warning(f"Theme directory does not exist: {self.css_directory}")
                return []
            
            # Find all *_theme.css files
            theme_files = list(css_path.glob("*_theme.css"))
            
            for theme_file in theme_files:
                theme_name = self._extract_theme_name(theme_file)
                if theme_name:
                    themes.append(theme_name)
                    
        except Exception as e:
            logger.error(f"Error discovering themes: {e}")
            # Fallback to cached theme detection
            return [name.replace('_theme', '').title() for name in self.css_cache.keys() if name.endswith('_theme')]
        
        return sorted(themes)
    
    def _extract_theme_name(self, theme_file: Path) -> str:
        """
        Extract theme name from CSS file.
        
        Tries in order:
        1. ThemeName=... comment
        2. Descriptive comment in first line
        3. Filename parsing
        """
        try:
            with open(theme_file, 'r', encoding='utf-8') as f:
                # Read first few lines to look for theme name
                first_lines = []
                for i, line in enumerate(f):
                    first_lines.append(line.strip())
                    if i >= 10:  # Only check first 10 lines
                        break
                
                # Method 1: Look for ThemeName=... comment
                for line in first_lines:
                    if 'ThemeName=' in line:
                        # Extract name after ThemeName=
                        start = line.find('ThemeName=') + len('ThemeName=')
                        end = line.find('*/', start) if '*/' in line[start:] else len(line)
                        theme_name = line[start:end].strip()
                        if theme_name:
                            return theme_name
                
                # Method 2: Extract from descriptive comment in first line
                if first_lines and first_lines[0].startswith('/*'):
                    comment = first_lines[0].replace('/*', '').replace('*/', '').strip()
                    # Look for patterns like "VS Code Dark+ Theme" or "Colorful Theme"
                    if 'Theme' in comment:
                        # Extract the main theme name (first significant word before "Theme")
                        parts = comment.split()
                        for i, part in enumerate(parts):
                            if 'Theme' in part:
                                # Take the word before "Theme" or the beginning part
                                if i > 0:
                                    potential_name = parts[i-1]
                                    # Handle compound names like "Dark+", "VS Code Dark+"
                                    if potential_name in ['Code', 'Studio']:
                                        # Look for pattern like "VS Code Dark+"
                                        if i > 1:
                                            potential_name = parts[i-1]
                                    # Clean up special characters
                                    clean_name = potential_name.replace('+', '').replace('-', '').strip()
                                    if clean_name:
                                        return clean_name.title()
                                elif 'Colorful' in comment:
                                    return 'Colorful'
                                elif 'Light' in comment:
                                    return 'Light'
                                elif 'Dark' in comment:
                                    return 'Dark'
                
                # Method 3: Parse filename as fallback
                filename = theme_file.stem  # Get filename without extension
                if filename.endswith('_theme'):
                    base_name = filename[:-6]  # Remove '_theme'
                    return base_name.replace('_', ' ').title()
                
        except Exception as e:
            logger.warning(f"Error extracting theme name from {theme_file}: {e}")
        
        # Ultimate fallback: use filename
        return theme_file.stem.replace('_theme', '').replace('_', ' ').title()
    
    def get_theme_filename(self, theme_name: str) -> str:
        """
        Get the CSS filename for a given theme name.
        
        This reverses the theme name extraction process.
        """
        try:
            css_path = Path(self.css_directory)
            theme_files = list(css_path.glob("*_theme.css"))
            
            for theme_file in theme_files:
                extracted_name = self._extract_theme_name(theme_file)
                if extracted_name == theme_name:
                    return theme_file.stem  # Return filename without extension
            
            # Fallback: convert theme name to expected filename pattern
            clean_name = theme_name.lower().replace(' ', '_')
            return f"{clean_name}_theme"
            
        except Exception as e:
            logger.warning(f"Error mapping theme name '{theme_name}' to filename: {e}")
            # Ultimate fallback
            clean_name = theme_name.lower().replace(' ', '_')
            return f"{clean_name}_theme"
    
    def has_css(self, name: str) -> bool:
        """Check if CSS exists for given name."""
        return name in self.css_cache
    
    def get_css_info(self) -> Dict[str, int]:
        """Get information about loaded CSS files."""
        return {name: len(content) for name, content in self.css_cache.items()}
    
    def get_current_css_file(self) -> str:
        """Get the path of the currently used CSS file for debugging."""
        return self.current_css_file
    
    def get_debug_info(self) -> Dict:
        """Get comprehensive debug information about CSS manager state."""
        return {
            "css_directory": self.css_directory,
            "current_css_file": self.current_css_file,
            "loaded_files": list(self.css_cache.keys()),
            "applied_styles": self.applied_styles.copy(),
            "file_sizes": self.get_css_info()
        }
