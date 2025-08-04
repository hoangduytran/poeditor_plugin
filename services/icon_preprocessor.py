"""
Icon Preprocessor for theme-aware icon generation.

This service processes SVG icons and generates CSS classes with Base64 encoded
SVG data that automatically adapts to the current theme colors.
"""

import base64
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from xml.etree import ElementTree as ET
from lg import logger


class IconPreprocessor:
    """
    Processes SVG icons for theme integration.
    
    Features:
    - Base64 SVG encoding for CSS embedding
    - Dynamic color replacement based on theme variables
    - CSS class generation for theme-aware icons
    - Icon optimization and validation
    """
    
    def __init__(self, icons_dir: str = "icons"):
        """
        Initialize the icon preprocessor.
        
        Args:
            icons_dir: Directory containing SVG icon files
        """
        self.icons_dir = Path(icons_dir)
        self.processed_icons: Dict[str, Dict[str, str]] = {}
        self.color_mappings: Dict[str, str] = {}
        
        # Initialize with default color mappings
        self._setup_default_color_mappings()
        
        logger.info(f"IconPreprocessor initialized with directory: {icons_dir}")
    
    def _setup_default_color_mappings(self):
        """Setup default color mappings for icon states."""
        self.color_mappings = {
            # Activity bar icon colors
            'activity-inactive': 'var(--color-activity-button-inactive)',
            'activity-hover': 'var(--color-activity-button-hover)', 
            'activity-active': 'var(--color-activity-button-active)',
            
            # General UI icon colors
            'icon-primary': 'var(--fg-main)',
            'icon-secondary': 'var(--fg-secondary)',
            'icon-muted': 'var(--color-text-muted)',
            'icon-accent': 'var(--accent-main)',
            
            # State-specific colors
            'icon-error': 'var(--color-error)',
            'icon-success': 'var(--color-accent-vs-code)',
            'icon-warning': 'var(--status-bar-modified-color)',
        }
    
    def process_svg_file(self, svg_path: Path) -> Optional[Dict[str, str]]:
        """
        Process a single SVG file and generate theme-aware variants.
        
        Args:
            svg_path: Path to the SVG file
            
        Returns:
            Dictionary with icon variants or None if processing failed
        """
        try:
            if not svg_path.exists():
                logger.error(f"SVG file not found: {svg_path}")
                return None
            
            # Read and parse SVG
            svg_content = svg_path.read_text(encoding='utf-8')
            
            # Extract icon name from filename
            icon_name = svg_path.stem
            
            # Generate variants for different states
            variants = {}
            
            # Determine state from filename
            if icon_name.endswith('_active'):
                base_name = icon_name[:-7]  # Remove '_active'
                variants['active'] = self._create_icon_variant(svg_content, 'activity-active')
            elif icon_name.endswith('_inactive'):
                base_name = icon_name[:-9]  # Remove '_inactive' 
                variants['inactive'] = self._create_icon_variant(svg_content, 'activity-inactive')
            else:
                base_name = icon_name
                # Generate multiple variants for this icon
                variants['primary'] = self._create_icon_variant(svg_content, 'icon-primary')
                variants['secondary'] = self._create_icon_variant(svg_content, 'icon-secondary')
                variants['muted'] = self._create_icon_variant(svg_content, 'icon-muted')
            
            # Store processed icon
            if base_name not in self.processed_icons:
                self.processed_icons[base_name] = {}
            self.processed_icons[base_name].update(variants)
            
            logger.debug(f"Processed SVG icon: {icon_name} -> {base_name} ({len(variants)} variants)")
            return variants
            
        except Exception as e:
            logger.error(f"Failed to process SVG file {svg_path}: {e}")
            return None
    
    def _create_icon_variant(self, svg_content: str, color_key: str) -> str:
        """
        Create an icon variant with the specified color mapping.
        
        Args:
            svg_content: Original SVG content
            color_key: Key for color mapping
            
        Returns:
            Base64 encoded SVG with theme variable colors
        """
        try:
            # Replace fill colors with CSS variables
            css_color = self.color_mappings.get(color_key, 'var(--fg-main)')
            
            # Replace fill attributes in SVG
            # This handles both fill="#ffffff" and fill="#858585" patterns
            modified_svg = re.sub(
                r'fill="[^"]*"',
                f'fill="{css_color}"',
                svg_content
            )
            
            # Ensure SVG is properly formatted and minified
            modified_svg = self._minify_svg(modified_svg)
            
            # Base64 encode for CSS embedding
            encoded = base64.b64encode(modified_svg.encode('utf-8')).decode('ascii')
            
            return encoded
            
        except Exception as e:
            logger.error(f"Failed to create icon variant with color {color_key}: {e}")
            return ""
    
    def _minify_svg(self, svg_content: str) -> str:
        """
        Minify SVG content for smaller CSS output.
        
        Args:
            svg_content: SVG content to minify
            
        Returns:
            Minified SVG content
        """
        try:
            # Parse and re-serialize to clean up formatting
            root = ET.fromstring(svg_content)
            
            # Remove unnecessary whitespace and comments
            ET.indent(root, space="", level=0)
            
            # Convert back to string
            minified = ET.tostring(root, encoding='unicode', method='xml')
            
            # Remove XML declaration and extra whitespace
            minified = re.sub(r'<\?xml[^>]*\?>', '', minified)
            minified = re.sub(r'\s+', ' ', minified)
            minified = minified.strip()
            
            return minified
            
        except Exception as e:
            logger.warning(f"SVG minification failed, using original: {e}")
            # Return original with basic cleanup
            return re.sub(r'\s+', ' ', svg_content).strip()
    
    def process_all_icons(self) -> Dict[str, Dict[str, str]]:
        """
        Process all SVG files in the icons directory.
        
        Returns:
            Dictionary of all processed icons with their variants
        """
        if not self.icons_dir.exists():
            logger.error(f"Icons directory not found: {self.icons_dir}")
            return {}
        
        processed_count = 0
        
        # Process all SVG files
        for svg_file in self.icons_dir.glob("*.svg"):
            result = self.process_svg_file(svg_file)
            if result:
                processed_count += 1
        
        logger.info(f"Processed {processed_count} SVG icons into {len(self.processed_icons)} icon sets")
        return self.processed_icons
    
    def generate_icon_css(self, generate_variables: bool = False, class_prefix: str = "icon-") -> str:
        """
        Generate CSS for all icons in the directory.
        
        Args:
            generate_variables: If True, generate CSS variables; if False, generate CSS classes
            class_prefix: Prefix for CSS class names (ignored if generate_variables=True)
        
        Returns:
            CSS string with icon variables/classes
        """
        # Ensure icons are processed before generating CSS
        if not self.processed_icons:
            logger.debug("Processing icons before CSS generation...")
            self.process_all_icons()
        
        if generate_variables:
            return self._generate_icon_variables()
        else:
            return self._generate_icon_classes(class_prefix)
    
    def _generate_icon_variables(self) -> str:
        """
        Generate CSS variables for all processed icons.
        This is used by activity_bar.css which expects var(--icon-*-url) format.
        
        Returns:
            CSS string with icon variables in :root selector
        """
        css_lines = [
            "/* Generated Icon CSS Variables */",
            "/* Auto-generated by IconPreprocessor - DO NOT EDIT MANUALLY */",
            "",
            ":root {",
            "    /* === ICON DATA URLS === */"
        ]
        
        for icon_name, variants in self.processed_icons.items():
            for variant_name, encoded_svg in variants.items():
                if not encoded_svg:
                    continue
                
                variable_name = f"--icon-{icon_name}-{variant_name}-url"
                data_url = f"url('data:image/svg+xml;base64,{encoded_svg}')"
                
                css_lines.append(f"    {variable_name}: {data_url};")
        
        css_lines.extend([
            "}",
            ""
        ])
        
        return "\n".join(css_lines)
    
    def _generate_icon_classes(self, class_prefix: str = "icon") -> str:
        """
        Generate CSS classes for all processed icons.
        
        Args:
            class_prefix: Prefix for CSS class names
            
        Returns:
            CSS string with icon classes
        """
        css_lines = [
            "/* Generated Icon CSS Classes */",
            "/* Auto-generated by IconPreprocessor - DO NOT EDIT MANUALLY */",
            ""
        ]
        
        for icon_name, variants in self.processed_icons.items():
            for variant_name, encoded_svg in variants.items():
                if not encoded_svg:
                    continue
                
                class_name = f"{class_prefix}-{icon_name}-{variant_name}"
                
                css_lines.extend([
                    f".{class_name} {{",
                    f"    background-image: url('data:image/svg+xml;base64,{encoded_svg}');",
                    f"    background-repeat: no-repeat;",
                    f"    background-position: center;",
                    f"    background-size: contain;",
                    f"}}",
                    ""
                ])
        
        return "\n".join(css_lines)
    
    def get_icon_data_url(self, icon_name: str, variant: str = "primary") -> Optional[str]:
        """
        Get the data URL for a specific icon variant.
        
        Args:
            icon_name: Name of the icon
            variant: Variant name (primary, secondary, muted, active, inactive)
            
        Returns:
            Data URL string or None if not found
        """
        try:
            encoded_svg = self.processed_icons.get(icon_name, {}).get(variant)
            if encoded_svg:
                return f"data:image/svg+xml;base64,{encoded_svg}"
            else:
                logger.warning(f"Icon variant not found: {icon_name}/{variant}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to get icon data URL for {icon_name}/{variant}: {e}")
            return None
    
    def update_color_mapping(self, color_key: str, css_variable: str):
        """
        Update or add a color mapping.
        
        Args:
            color_key: Key for the color mapping
            css_variable: CSS variable to map to
        """
        self.color_mappings[color_key] = css_variable
        logger.debug(f"Updated color mapping: {color_key} -> {css_variable}")
    
    def get_available_icons(self) -> List[str]:
        """
        Get list of available icon names.
        
        Returns:
            List of icon names
        """
        return list(self.processed_icons.keys())
    
    def get_icon_variants(self, icon_name: str) -> List[str]:
        """
        Get available variants for a specific icon.
        
        Args:
            icon_name: Name of the icon
            
        Returns:
            List of variant names
        """
        return list(self.processed_icons.get(icon_name, {}).keys())
