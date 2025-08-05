"""
Import/Export infrastructure for preferences system.

This module provides file format handlers and import/export functionality
for preference data, supporting multiple formats like JSON, CSV, PLIST, etc.
"""

import json
import csv
import os
from pathlib import Path
from typing import List, Dict, Any, Optional, Type, Union
from abc import ABC, abstractmethod
from datetime import datetime
import tempfile

from lg import logger
from .data_models import ReplacementRecord, DatabasePORecord


class BaseFormatHandler(ABC):
    """Base class for import/export format handlers."""
    
    @property
    @abstractmethod
    def format_name(self) -> str:
        """Name of the format."""
        pass
    
    @property
    @abstractmethod
    def file_extensions(self) -> List[str]:
        """Supported file extensions."""
        pass
    
    @property
    @abstractmethod
    def supports_import(self) -> bool:
        """Whether this handler supports import."""
        pass
    
    @property
    @abstractmethod
    def supports_export(self) -> bool:
        """Whether this handler supports export."""
        pass
    
    @abstractmethod
    def import_data(self, file_path: str) -> List[Any]:
        """Import data from file."""
        pass
    
    @abstractmethod
    def export_data(self, data: List[Any], file_path: str) -> bool:
        """Export data to file."""
        pass
    
    def validate_file(self, file_path: str) -> bool:
        """Validate file format before import."""
        return Path(file_path).exists()


class JsonHandler(BaseFormatHandler):
    """JSON format handler for replacement rules and history."""
    
    @property
    def format_name(self) -> str:
        return "JSON"
    
    @property
    def file_extensions(self) -> List[str]:
        return [".json"]
    
    @property
    def supports_import(self) -> bool:
        return True
    
    @property
    def supports_export(self) -> bool:
        return True
    
    def import_data(self, file_path: str) -> List[Dict[str, Any]]:
        """Import data from JSON file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Handle both single object and array formats
            if isinstance(data, dict):
                if 'records' in data:
                    return data['records']
                else:
                    return [data]
            elif isinstance(data, list):
                return data
            else:
                logger.error(f"Invalid JSON format in {file_path}")
                return []
                
        except Exception as e:
            logger.error(f"Failed to import JSON from {file_path}: {e}")
            return []
    
    def export_data(self, data: List[Any], file_path: str) -> bool:
        """Export data to JSON file."""
        try:
            # Convert records to dictionaries
            export_data = []
            for item in data:
                try:
                    # Try to_dict() method first
                    export_data.append(item.to_dict())
                except AttributeError:
                    if isinstance(item, dict):
                        export_data.append(item)
                    else:
                        # Convert to dict manually
                        export_data.append(self._to_dict(item))
            
            # Create export structure
            output = {
                'format': 'POEditor Preferences Export',
                'version': '1.0',
                'exported_at': datetime.now().isoformat(),
                'count': len(export_data),
                'records': export_data
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(output, f, indent=2, ensure_ascii=False, default=str)
            
            logger.info(f"Exported {len(export_data)} records to {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to export JSON to {file_path}: {e}")
            return False
    
    def _to_dict(self, obj: Any) -> Dict[str, Any]:
        """Convert object to dictionary."""
        if isinstance(obj, dict):
            return obj
        
        # Use object's __dict__ as fallback
        result = {}
        for key, value in obj.__dict__.items():
            if not key.startswith('_'):
                result[key] = value
        return result


class CsvHandler(BaseFormatHandler):
    """CSV format handler for replacement rules."""
    
    @property
    def format_name(self) -> str:
        return "CSV"
    
    @property
    def file_extensions(self) -> List[str]:
        return [".csv"]
    
    @property
    def supports_import(self) -> bool:
        return True
    
    @property
    def supports_export(self) -> bool:
        return True
    
    def import_data(self, file_path: str) -> List[Dict[str, Any]]:
        """Import data from CSV file."""
        try:
            records = []
            with open(file_path, 'r', encoding='utf-8', newline='') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Convert string boolean values
                    for key in ['enabled', 'case_sensitive', 'use_regex', 'fuzzy']:
                        if key in row:
                            row[key] = row[key].lower() in ('true', '1', 'yes', 'on')
                    
                    records.append(row)
            
            logger.info(f"Imported {len(records)} records from {file_path}")
            return records
            
        except Exception as e:
            logger.error(f"Failed to import CSV from {file_path}: {e}")
            return []
    
    def export_data(self, data: List[Any], file_path: str) -> bool:
        """Export data to CSV file."""
        try:
            if not data:
                logger.warning("No data to export")
                return False
            
            # Convert to dictionaries
            dict_data = []
            for item in data:
                try:
                    dict_data.append(item.to_dict())
                except AttributeError:
                    if isinstance(item, dict):
                        dict_data.append(item)
                    else:
                        dict_data.append(self._to_dict(item))
            
            # Get fieldnames from first record
            fieldnames = list(dict_data[0].keys())
            
            with open(file_path, 'w', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(dict_data)
            
            logger.info(f"Exported {len(dict_data)} records to {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to export CSV to {file_path}: {e}")
            return False
    
    def _to_dict(self, obj: Any) -> Dict[str, Any]:
        """Convert object to dictionary."""
        if isinstance(obj, dict):
            return obj
        
        result = {}
        for key, value in obj.__dict__.items():
            if not key.startswith('_'):
                result[key] = value
        return result


class PlistHandler(BaseFormatHandler):
    """PLIST (Property List) format handler for macOS compatibility."""
    
    @property
    def format_name(self) -> str:
        return "PLIST"
    
    @property
    def file_extensions(self) -> List[str]:
        return [".plist"]
    
    @property
    def supports_import(self) -> bool:
        return True
    
    @property
    def supports_export(self) -> bool:
        return True
    
    def import_data(self, file_path: str) -> List[Dict[str, Any]]:
        """Import data from PLIST file."""
        try:
            import plistlib
            
            with open(file_path, 'rb') as f:
                data = plistlib.load(f)
            
            # Handle different PLIST structures
            if isinstance(data, dict) and 'records' in data:
                return data['records']
            elif isinstance(data, list):
                return data
            elif isinstance(data, dict):
                return [data]
            else:
                logger.error(f"Invalid PLIST format in {file_path}")
                return []
                
        except ImportError:
            logger.error("plistlib not available for PLIST import")
            return []
        except Exception as e:
            logger.error(f"Failed to import PLIST from {file_path}: {e}")
            return []
    
    def export_data(self, data: List[Any], file_path: str) -> bool:
        """Export data to PLIST file."""
        try:
            import plistlib
            
            # Convert to dictionaries
            export_data = []
            for item in data:
                try:
                    export_data.append(item.to_dict())
                except AttributeError:
                    if isinstance(item, dict):
                        export_data.append(item)
                    else:
                        export_data.append(self._to_dict(item))
            
            # Create PLIST structure
            plist_data = {
                'format': 'POEditor Preferences Export',
                'version': '1.0',
                'exported_at': datetime.now().isoformat(),
                'records': export_data
            }
            
            with open(file_path, 'wb') as f:
                plistlib.dump(plist_data, f)
            
            logger.info(f"Exported {len(export_data)} records to {file_path}")
            return True
            
        except ImportError:
            logger.error("plistlib not available for PLIST export")
            return False
        except Exception as e:
            logger.error(f"Failed to export PLIST to {file_path}: {e}")
            return False
    
    def _to_dict(self, obj: Any) -> Dict[str, Any]:
        """Convert object to dictionary."""
        if isinstance(obj, dict):
            return obj
        
        result = {}
        for key, value in obj.__dict__.items():
            if not key.startswith('_'):
                # Convert datetime objects to strings for PLIST compatibility
                if isinstance(value, datetime):
                    result[key] = value.isoformat()
                else:
                    result[key] = value
        return result


class YamlHandler(BaseFormatHandler):
    """YAML format handler for human-readable exports."""
    
    @property
    def format_name(self) -> str:
        return "YAML"
    
    @property
    def file_extensions(self) -> List[str]:
        return [".yaml", ".yml"]
    
    @property
    def supports_import(self) -> bool:
        return True
    
    @property
    def supports_export(self) -> bool:
        return True
    
    def import_data(self, file_path: str) -> List[Dict[str, Any]]:
        """Import data from YAML file."""
        try:
            import yaml
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            if isinstance(data, dict) and 'records' in data:
                return data['records']
            elif isinstance(data, list):
                return data
            elif isinstance(data, dict):
                return [data]
            else:
                logger.error(f"Invalid YAML format in {file_path}")
                return []
                
        except ImportError:
            logger.error("PyYAML not available for YAML import")
            return []
        except Exception as e:
            logger.error(f"Failed to import YAML from {file_path}: {e}")
            return []
    
    def export_data(self, data: List[Any], file_path: str) -> bool:
        """Export data to YAML file."""
        try:
            import yaml
            
            # Convert to dictionaries
            export_data = []
            for item in data:
                try:
                    export_data.append(item.to_dict())
                except AttributeError:
                    if isinstance(item, dict):
                        export_data.append(item)
                    else:
                        export_data.append(self._to_dict(item))
            
            # Create YAML structure
            output = {
                'format': 'POEditor Preferences Export',
                'version': '1.0',
                'exported_at': datetime.now().isoformat(),
                'records': export_data
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                yaml.dump(output, f, default_flow_style=False, 
                         allow_unicode=True, indent=2)
            
            logger.info(f"Exported {len(export_data)} records to {file_path}")
            return True
            
        except ImportError:
            logger.error("PyYAML not available for YAML export")
            return False
        except Exception as e:
            logger.error(f"Failed to export YAML to {file_path}: {e}")
            return False
    
    def _to_dict(self, obj: Any) -> Dict[str, Any]:
        """Convert object to dictionary."""
        if isinstance(obj, dict):
            return obj
        
        result = {}
        for key, value in obj.__dict__.items():
            if not key.startswith('_'):
                result[key] = value
        return result


class ImportExportService:
    """Service for managing import/export operations."""
    
    def __init__(self):
        self.handlers: Dict[str, BaseFormatHandler] = {}
        self._register_default_handlers()
        logger.info("ImportExportService initialized")
    
    def _register_default_handlers(self):
        """Register default format handlers."""
        handlers = [
            JsonHandler(),
            CsvHandler(),
            PlistHandler(),
            YamlHandler()
        ]
        
        for handler in handlers:
            self.register_handler(handler)
    
    def register_handler(self, handler: BaseFormatHandler):
        """Register a format handler."""
        for ext in handler.file_extensions:
            self.handlers[ext.lower()] = handler
        logger.debug(f"Registered handler for {handler.format_name}: {handler.file_extensions}")
    
    def get_supported_formats(self, operation: str = 'both') -> Dict[str, List[str]]:
        """Get supported formats for import/export."""
        formats = {}
        
        for ext, handler in self.handlers.items():
            if operation == 'import' and not handler.supports_import:
                continue
            if operation == 'export' and not handler.supports_export:
                continue
            
            format_name = handler.format_name
            if format_name not in formats:
                formats[format_name] = []
            formats[format_name].append(ext)
        
        return formats
    
    def get_file_filter_string(self, operation: str = 'both') -> str:
        """Get file filter string for dialogs."""
        formats = self.get_supported_formats(operation)
        filters = []
        
        for format_name, extensions in formats.items():
            ext_pattern = ' '.join(f'*{ext}' for ext in extensions)
            filters.append(f"{format_name} ({ext_pattern})")
        
        filters.append("All Files (*)")
        return ';;'.join(filters)
    
    def import_file(self, file_path: str, record_type: Optional[Type] = None) -> List[Any]:
        """Import data from file."""
        ext = Path(file_path).suffix.lower()
        handler = self.handlers.get(ext)
        
        if not handler:
            logger.error(f"No handler for file extension: {ext}")
            return []
        
        if not handler.supports_import:
            logger.error(f"Handler for {ext} does not support import")
            return []
        
        try:
            raw_data = handler.import_data(file_path)
            
            # Convert to record objects if record_type provided
            if record_type and raw_data:
                records = []
                for item in raw_data:
                    if isinstance(item, dict):
                        try:
                            record = record_type.from_dict(item)
                            records.append(record)
                        except Exception as e:
                            logger.warning(f"Failed to convert record: {e}")
                    else:
                        records.append(item)
                return records
            
            return raw_data
            
        except Exception as e:
            logger.error(f"Import failed: {e}")
            return []
    
    def export_file(self, data: List[Any], file_path: str) -> bool:
        """Export data to file."""
        ext = Path(file_path).suffix.lower()
        handler = self.handlers.get(ext)
        
        if not handler:
            logger.error(f"No handler for file extension: {ext}")
            return False
        
        if not handler.supports_export:
            logger.error(f"Handler for {ext} does not support export")
            return False
        
        # Create backup if file exists
        if Path(file_path).exists():
            backup_path = f"{file_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            try:
                import shutil
                shutil.copy2(file_path, backup_path)
                logger.info(f"Created backup: {backup_path}")
            except Exception as e:
                logger.warning(f"Failed to create backup: {e}")
        
        return handler.export_data(data, file_path)
    
    def validate_import_file(self, file_path: str) -> bool:
        """Validate file before import."""
        ext = Path(file_path).suffix.lower()
        handler = self.handlers.get(ext)
        
        if not handler:
            return False
        
        return handler.validate_file(file_path)


class ImportExportWidget:
    """UI widget helper for import/export operations (future implementation)."""
    
    def __init__(self, service: ImportExportService):
        self.service = service
        logger.debug("ImportExportWidget helper created")
    
    def get_import_file_dialog_filter(self) -> str:
        """Get filter string for import file dialog."""
        return self.service.get_file_filter_string('import')
    
    def get_export_file_dialog_filter(self) -> str:
        """Get filter string for export file dialog."""
        return self.service.get_file_filter_string('export')
    
    def validate_and_import(self, file_path: str, record_type: Optional[Type] = None) -> List[Any]:
        """Validate and import file with user feedback."""
        if not self.service.validate_import_file(file_path):
            logger.error(f"Invalid import file: {file_path}")
            return []
        
        return self.service.import_file(file_path, record_type)
