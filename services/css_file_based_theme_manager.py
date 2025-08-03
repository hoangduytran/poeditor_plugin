"""
Theme Manager for the POEditor Application.

Manages theme loading, switching, and application.
Now supports both file-based CSS and resource-based CSS with fallback.
"""

import os
from typing import Optional, Dict
from PySide6.QtCore import QFile, QIODevice, QObject, Signal, QSettings
from PySide6.QtWidgets import QApplication
from .css_manager import CSSManager
from .css_preprocessor import CSSPreprocessor
from lg import logger

# Simple Theme class for compatibility
class Theme:
    def __init__(self, name: str):
        self.name = name
        self.dark_mode = name.lower() == 'dark'

class CSSFileBasedThemeManager(QObject):
    """
    Manages the application's theme, including loading, switching, and applying themes.
    Supports both file-based CSS themes and resource-based themes with fallback.
    """
    
    # Signals
    theme_changed = Signal(str)  # Emitted when theme changes
    theme_applied = Signal(str)  # Emitted when CSS is applied
    
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(CSSFileBasedThemeManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        # Prevent double initialization for QObject
        if hasattr(self, '_initialized') and self._initialized:
            return
            
        super().__init__()  # Initialize QObject
        self._initialized = True
        
        self.current_theme = None
        self.css_manager = None
        self.css_preprocessor = None
        self.use_file_css = False
        
        # CSS cache for fast theme switching
        self._css_cache = {}
        self._cache_loaded = False
        
        # Initialize settings for theme persistence
        self.settings = QSettings('POEditor', 'ThemeManager')

        # Initialize CSS Manager for file-based CSS loading
        logger.debug("About to initialize CSS Manager...")
        try:
            self.css_manager = CSSManager()
            self.css_preprocessor = CSSPreprocessor("themes")
            logger.debug(f"CSS Manager created, cache size: {len(self.css_manager.css_cache)}")
            self.use_file_css = len(self.css_manager.css_cache) > 0
            if self.use_file_css:
                logger.info("ThemeManager using file-based CSS system with CSS preprocessor")
            else:
                logger.info("ThemeManager falling back to resource-based CSS system")
        except Exception as e:
            logger.error(f"Failed to initialize CSS Manager, using resources: {e}")
            self.css_manager = None
            self.css_preprocessor = None
            self.use_file_css = False
            
        # Load saved theme (but don't apply it yet - wait for application setup)
        self._restore_saved_theme_name()
        
        # Pre-load CSS cache for faster theme switching
        self._preload_css_cache()

    def set_theme(self, theme_name: str):
        """
        Set and apply the theme by name with optimized performance.

        Args:
            theme_name (str): The name of the theme to apply.
        """
        # Debug current state before applying theme
        logger.info(f"=== THEME DEBUG: set_theme({theme_name}) ===")
        logger.info(f"Current theme state: {self.current_theme}")
        logger.info(f"Requested theme: {theme_name}")
        
        # Check if theme is already active
        if self.current_theme == theme_name:
            logger.debug(f"Theme {theme_name} is already active, skipping...")
            return
            
        old_theme = self.current_theme
        self.current_theme = theme_name
        
        # Map theme name to file name using CSS manager
        theme_file_name = self._get_theme_filename(theme_name)

        # Load and apply the theme CSS (now cached for speed)
        css_content = self._load_theme_css(theme_file_name)
        if css_content:
            self._apply_theme(css_content)
            
            # Save the current theme to settings (optimized - no sync)
            self._save_current_theme()
            
            # Emit theme changed signal if theme actually changed
            if old_theme != theme_name:
                self.theme_changed.emit(theme_name)
        else:
            logger.error(f"Failed to load CSS for theme: {theme_name}")
            # Revert current_theme if CSS loading failed
            self.current_theme = old_theme

    def _load_theme_css(self, theme_file_name: str) -> str:
        """Load theme CSS content with caching for fast switching."""
        logger.info(f"=== CSS TRACE: _load_theme_css called for theme_file_name: {theme_file_name} ===")
        # Check cache first for instant loading
        if theme_file_name in self._css_cache:
            logger.info(f"=== CSS TRACE: Found theme in cache: {theme_file_name}, length: {len(self._css_cache[theme_file_name])} ===")
            return self._css_cache[theme_file_name]
        
        # Cache miss - load and cache for next time
        logger.info(f"=== CSS TRACE: Cache miss for theme: {theme_file_name}, loading from source... ===")
        css_content = self._load_theme_css_uncached(theme_file_name)
        logger.info(f"=== CSS TRACE: Loaded CSS content for {theme_file_name}, length: {len(css_content) if css_content else 0} ===")
        if css_content:
            self._css_cache[theme_file_name] = css_content
            logger.info(f"Loaded and cached theme CSS: {theme_file_name} ({len(css_content)} chars)")
        return css_content

    def _apply_theme(self, css_content: str):
        """Apply theme CSS to the application."""
        try:
            app = QApplication.instance()
            if not app:
                logger.error("No QApplication instance found for theme application")
                return
                
            # Add explicit type check for Pylance
            if not isinstance(app, QApplication):
                logger.error("Application instance is not QApplication")
                return
            
            # Debug logging before applying theme
            logger.info(f"=== THEME APPLICATION DEBUG ===")
            logger.info(f"Applying theme: {self.current_theme}")
            logger.info(f"CSS content length: {len(css_content)} chars")
            logger.info(f"CSS preview (first 200 chars): {css_content[:200]}")
            
            # Try to extract background color from CSS
            import re
            bg_color_match = re.search(r'background(-color)?\s*:\s*(#[0-9a-fA-F]{6})', css_content)
            if bg_color_match:
                css_bg_color = bg_color_match.group(2)
                logger.info(f"Found CSS background color: {css_bg_color}")
            
            # Get current widget colors before applying (for debugging only)
            from PySide6.QtGui import QPalette, QColor
            window_color = app.palette().color(QPalette.ColorRole.Window)
            text_color = app.palette().color(QPalette.ColorRole.WindowText)
            logger.info(f"BEFORE - Background: {window_color.name()}, Text: {text_color.name()}")
            
            # Reset palette to system defaults to ensure CSS has full control
            app.setPalette(QPalette())
            logger.info("Reset palette to system defaults to let CSS control all styling")
            
            # Apply stylesheet directly - let CSS control all colors
            logger.info(f"Applying theme CSS directly without palette manipulation")
            
            # Process CSS variables using preprocessor if available
            processed_css = css_content
            if self.css_preprocessor:
                try:
                    # Load variables.css file if it exists
                    variables_css = ""
                    if self.css_manager and "variables" in self.css_manager.css_cache:
                        variables_css = self.css_manager.css_cache["variables"]
                        logger.debug("Found variables.css file, including in processing")
                    
                    # Combine variables CSS with theme CSS
                    combined_css = variables_css + "\n" + css_content
                    
                    # Extract variables from the combined CSS content
                    variables = self.css_preprocessor.extract_variables(combined_css)
                    logger.debug(f"Extracted {len(variables)} CSS variables")
                    
                    # Process CSS to replace var() references with actual values
                    processed_css = self.css_preprocessor.process_css(combined_css, variables)
                    logger.info(f"CSS preprocessing completed successfully")
                    logger.debug(f"Processed CSS preview (first 200 chars): {processed_css[:200]}")
                    
                    # Debug: Write processed CSS to a file for inspection
                    try:
                        debug_file = f"debug_processed_{self.current_theme.lower() if self.current_theme else 'unknown'}_theme.css"
                        with open(debug_file, 'w', encoding='utf-8') as f:
                            f.write(processed_css)
                        logger.info(f"Debug: Processed CSS written to {debug_file}")
                    except Exception as debug_e:
                        logger.warning(f"Failed to write debug CSS file: {debug_e}")
                except Exception as e:
                    logger.error(f"CSS preprocessing failed: {e}")
                    processed_css = css_content  # Fallback to original CSS
            else:
                logger.warning("CSS preprocessor not available, using CSS as-is")
            
            app.setStyleSheet(processed_css)
            
            # Log for debugging that CSS has been applied
            logger.info(f"CSS has been applied for theme: {self.current_theme}")
                
            self.theme_applied.emit(self.current_theme or "")
            logger.info(f"Applied theme CSS: {self.current_theme}")
        except Exception as e:
            logger.error(f"Failed to apply theme CSS: {e}")

    def reload_current_theme(self) -> bool:
        """Reload the current theme from disk (file-based CSS only)."""
        if not self.use_file_css or not self.css_manager:
            logger.warning("Reload not available - using resource-based CSS")
            return False
        
        if not self.current_theme:
            logger.warning("No current theme to reload")
            return False
        
        try:
            # Clear cache for the current theme to force reload
            theme_file_name = self._get_theme_filename(self.current_theme)
            if theme_file_name in self._css_cache:
                del self._css_cache[theme_file_name]
                logger.debug(f"Cleared cache for theme: {self.current_theme}")
            
            # Reload the CSS file
            if self.css_manager.reload_css_file(theme_file_name):
                # Force reapply the theme by temporarily clearing current_theme
                current_theme_name = self.current_theme
                self.current_theme = None  # Force reload by clearing current theme
                self.set_theme(current_theme_name)
                logger.info(f"Successfully reloaded theme: {current_theme_name}")
                return True
            else:
                logger.error(f"Failed to reload theme file: {theme_file_name}")
                return False
        except Exception as e:
            logger.error(f"Error reloading theme: {e}")
            return False

    def get_raw_css(self, theme_name: str) -> Optional[str]:
        """Get raw CSS content for debugging."""
        theme_file_name = self._get_theme_filename(theme_name)
        
        if self.use_file_css and self.css_manager:
            return self.css_manager.get_css(theme_file_name)
        else:
            # Fallback to loading from resources
            return self._load_theme_css(theme_file_name)

    def inject_css(self, css_snippet: str, temporary: bool = True) -> bool:
        """Inject custom CSS snippet (development feature)."""
        try:
            app = QApplication.instance()  # Pylance thinks this is QCoreApplication
            if not app:
                logger.error("No QApplication instance for CSS injection")
                return False
            
            # Add explicit type checking/casting to tell Pylance it's a QApplication
            if not isinstance(app, QApplication):
                logger.error("Application instance is not QApplication")
                return False
                
            if temporary:
                # Append to current stylesheet
                current_css = app.styleSheet()
                new_css = f"{current_css}\n\n/* Injected CSS */\n{css_snippet}"
                app.setStyleSheet(new_css)
            else:
                # Replace stylesheet entirely
                app.setStyleSheet(css_snippet)
            
            logger.info("CSS injection successful")
            return True
            
        except Exception as e:
            logger.error(f"CSS injection failed: {e}")
            return False

    def get_css_manager_info(self) -> Dict:
        """Get information about CSS manager state."""
        info = {
            "use_file_css": self.use_file_css,
            "css_manager_available": self.css_manager is not None,
            "current_theme": self.current_theme
        }
        
        if self.css_manager:
            info["loaded_css_files"] = self.css_manager.get_css_info()
            info["available_themes"] = self.css_manager.get_available_themes()
        
        return info

    def get_available_themes(self) -> list:
        """Get list of available themes by dynamically discovering CSS files."""
        if self.use_file_css and self.css_manager:
            # Use CSS manager's dynamic theme discovery
            return self.css_manager.get_available_themes()
        else:
            # Fallback to only the 3 main themes for resource-based CSS
            return ["Dark", "Light", "Colorful"]
    
    def _get_theme_filename(self, theme_name: str) -> str:
        """Get the CSS filename for a given theme name."""
        if self.use_file_css and self.css_manager:
            return self.css_manager.get_theme_filename(theme_name)
        else:
            # Fallback for resource-based CSS
            return f"{theme_name.lower()}_theme"

    def get_current_theme(self) -> Optional[Theme]:
        """Get the currently applied theme as a Theme object."""
        if self.current_theme:
            return Theme(self.current_theme)
        return None
        
    def apply_activity_bar_theme(self, widget) -> bool:
        """Apply activity bar specific theme with CSS variable processing."""
        try:
            if self.use_file_css and self.css_manager:
                activity_css = self.css_manager.get_css('activity_bar')
                if activity_css:
                    # Process CSS variables if preprocessor is available
                    if self.css_preprocessor:
                        # Get variables from the current theme
                        variables = {}
                        
                        # Get variables from variables.css if available
                        if self.css_manager and hasattr(self.css_manager, 'css_cache') and "variables" in self.css_manager.css_cache:
                            variables_css = self.css_manager.css_cache["variables"]
                            variables.update(self.css_preprocessor.extract_variables(variables_css))
                        
                        # Get variables from current theme CSS if we have a current theme
                        if self.current_theme:
                            theme_file_name = self._get_theme_filename(self.current_theme)
                            if theme_file_name in self._css_cache:
                                theme_css = self._css_cache[theme_file_name]
                                variables.update(self.css_preprocessor.extract_variables(theme_css))
                        
                        # Process ActivityBar CSS with variables
                        processed_css = self.css_preprocessor.process_css(activity_css, variables)
                        widget.setStyleSheet(processed_css)
                        logger.info(f"Applied processed activity bar theme to widget: {widget.objectName()}")
                        logger.debug(f"ActivityBar CSS processed with {len(variables)} variables")
                    else:
                        # Fallback to raw CSS if no preprocessor
                        widget.setStyleSheet(activity_css)
                        logger.info(f"Applied raw activity bar theme to widget: {widget.objectName()}")
                    return True
            
            # Fallback to resource-based CSS
            file = QFile(":/themes/css/activity_bar.css")
            if file.open(QIODevice.OpenModeFlag.ReadOnly):
                # Fix: Use .data() to get bytes and then decode
                byte_array = file.readAll()
                content = bytes(byte_array.data()).decode('utf-8')
                file.close()
                
                # Process CSS variables if preprocessor is available
                if self.css_preprocessor:
                    variables = {}
                    
                    # Get variables from variables.css if available
                    if self.css_manager and hasattr(self.css_manager, 'css_cache') and "variables" in self.css_manager.css_cache:
                        variables_css = self.css_manager.css_cache["variables"]
                        variables.update(self.css_preprocessor.extract_variables(variables_css))
                    
                    # Get variables from current theme if available
                    if self.current_theme:
                        theme_file_name = self._get_theme_filename(self.current_theme)
                        if theme_file_name in self._css_cache:
                            theme_css = self._css_cache[theme_file_name]
                            variables.update(self.css_preprocessor.extract_variables(theme_css))
                    
                    processed_css = self.css_preprocessor.process_css(content, variables)
                    widget.setStyleSheet(processed_css)
                    logger.info(f"Applied processed activity bar theme from resource to widget: {widget.objectName()}")
                    logger.debug(f"ActivityBar CSS processed with {len(variables)} variables from resource")
                else:
                    widget.setStyleSheet(content)
                    logger.info(f"Applied raw activity bar theme from resource to widget: {widget.objectName()}")
                return True
            else:
                logger.error("Failed to open activity bar CSS resource")
                return False
        except Exception as e:
            logger.error(f"Error applying activity bar theme: {e}")
            return False

    def get_style_for_component(self, component_name: str) -> Dict:
        """Get style information for a specific component."""
        if component_name == "tabs":
            return {
                "background_color": "#1e1e1e",
                "border_color": "#464647",
                "text_color": "#cccccc" 
            }
        elif component_name == "tab_active":
            return {
                "background_color": "#1e1e1e",
                "text_color": "#ffffff",
                "border_color": "#007acc"
            }
        elif component_name == "tab_inactive":
            return {
                "background_color": "#2d2d30",
                "text_color": "#969696",
                "border_color": "#464647"
            }
        elif component_name == "tab_hover":
            return {
                "background_color": "#2a2d2e",
                "text_color": "#cccccc",
                "border_color": "#464647"
            }
        else:
            # Default style
            return {
                "background_color": "#252526",
                "text_color": "#cccccc",
                "border_color": "#464647"
            }

    def toggle_theme(self) -> str:
        """Toggle between available themes in a cycle."""
        available_themes = self.get_available_themes()
        if not available_themes:
            return self.current_theme or "Dark"
        
        current_theme = self.current_theme or "Dark"
        try:
            current_index = available_themes.index(current_theme)
        except ValueError:
            current_index = -1
        
        next_index = (current_index + 1) % len(available_themes)
        next_theme = available_themes[next_index]
        
        self.set_theme(next_theme)
        return next_theme

    def refresh_theme(self) -> bool:
        """Refresh the current theme (reload and reapply)."""
        if not self.current_theme:
            return False
        
        # Reload the theme if using file-based CSS
        if self.use_file_css and self.css_manager:
            theme_file_name = f"{self.current_theme.lower()}_theme"
            self.css_manager.reload_css_file(theme_file_name)
        
        # Reapply the theme
        self.set_theme(self.current_theme)
        return True
        
    def _apply_dark_palette(self, app: QApplication) -> None:
        """
        Previously applied a dark palette, now a no-op to let CSS control all styling.
        """
        # No-op function - letting CSS control all styling
        logger.debug("Dark palette application skipped - using CSS only")
        pass
        
    def _apply_light_palette(self, app: QApplication) -> None:
        """
        Previously applied a light palette, now a no-op to let CSS control all styling.
        """
        # No-op function - letting CSS control all styling
        logger.debug("Light palette application skipped - using CSS only")
        pass


    @classmethod
    def get_instance(cls):
        """Get the singleton instance of CSSFileBasedThemeManager."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def _load_saved_theme(self):
        """Load the saved theme from settings and apply it."""
        try:
            saved_theme = self.settings.value('current_theme', 'Light')
            if isinstance(saved_theme, str) and saved_theme in self.get_available_themes():
                logger.info(f"Loading saved theme: {saved_theme}")
                self.current_theme = saved_theme
                # Apply the saved theme
                theme_file_name = f"{saved_theme.lower()}_theme"
                css_content = self._load_theme_css(theme_file_name)
                self._apply_theme(css_content)
            else:
                logger.info("No valid saved theme found, using default Light theme")
                self.set_theme('Light')
        except Exception as e:
            logger.error(f"Error loading saved theme: {e}")
            # Fallback to Light theme
            self.set_theme('Light')
    
    def _restore_saved_theme_name(self):
        """Restore the saved theme name only (without applying CSS)."""
        try:
            saved_theme = self.settings.value('current_theme', 'Light')
            if isinstance(saved_theme, str) and saved_theme in self.get_available_themes():
                logger.info(f"Restored saved theme name: {saved_theme}")
                self.current_theme = saved_theme
                return saved_theme
            else:
                logger.info("No valid saved theme found, defaulting to Light theme")
                self.current_theme = 'Light'
                return 'Light'
        except Exception as e:
            logger.error(f"Error restoring saved theme name: {e}")
            self.current_theme = 'Light'
            return 'Light'
    
    def apply_saved_theme(self):
        """Apply the saved theme from settings."""
        logger.info("CSSFileBasedThemeManager: Applying saved theme")
        
        # Restore the saved theme name and apply it
        saved_theme = self._restore_saved_theme_name()
        if saved_theme:
            logger.info(f"Restored saved theme name: {saved_theme}")
            # Force application by clearing current_theme first (since nothing is visually applied yet)
            self.current_theme = None
            self.set_theme(saved_theme)
        else:
            logger.info("No saved theme found, using default")
            self.current_theme = None
            self.set_theme('Light')
    
    def _save_current_theme(self):
        """Save the current theme to settings."""
        try:
            if self.current_theme:
                self.settings.setValue('current_theme', self.current_theme)
                # Remove sync() for faster theme switching - Qt will sync automatically
                logger.debug(f"Saved current theme: {self.current_theme}")
        except Exception as e:
            logger.error(f"Error saving current theme: {e}")
    
    def _preload_css_cache(self):
        """Pre-load all theme CSS files into memory for faster switching."""
        if self._cache_loaded:
            return
            
        logger.debug("Pre-loading CSS cache for faster theme switching...")
        available_themes = self.get_available_themes()
        
        for theme_name in available_themes:
            theme_file_name = self._get_theme_filename(theme_name)
            try:
                css_content = self._load_theme_css_uncached(theme_file_name)
                if css_content:
                    self._css_cache[theme_file_name] = css_content
                    logger.debug(f"Cached CSS for theme: {theme_name} ({len(css_content)} chars)")
            except Exception as e:
                logger.warning(f"Failed to cache CSS for theme {theme_name}: {e}")
        
        self._cache_loaded = True
        logger.info(f"CSS cache loaded with {len(self._css_cache)} themes")
    
    def _load_theme_css_uncached(self, theme_file_name: str) -> str:
        """Load theme CSS without using cache (for initial cache population)."""
        base_css_content = ""
        component_css = []
        
        # Try file-based CSS first
        if self.use_file_css and self.css_manager:
            # Get the base theme CSS
            base_css_content = self.css_manager.get_css(theme_file_name) or ""
            
            # Add component CSS
            context_menu_css = self.css_manager.get_css("context_menu") or ""
            if context_menu_css:
                component_css.append(context_menu_css)
                
            # Common CSS should come LAST for highest priority (especially status bar styles)
            common_css = self.css_manager.get_css("common") or ""
            if common_css:
                component_css.append(common_css)
        
        # Fallback to resource-based CSS if file-based failed
        if not base_css_content:
            try:
                file = QFile(f":/themes/css/{theme_file_name}.css")
                if file.open(QIODevice.OpenModeFlag.ReadOnly):
                    byte_array = file.readAll()
                    base_css_content = bytes(byte_array.data()).decode('utf-8')
                    file.close()
            except Exception as e:
                logger.error(f"Error loading resource-based CSS for {theme_file_name}: {e}")
        
        # Combine CSS: theme first, then components (including common.css last)
        full_css = base_css_content
        for css in component_css:
            full_css += "\n\n" + css
            
        return full_css
    
