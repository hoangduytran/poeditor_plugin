==============================
Service Development Guide
==============================

.. py:module:: guides.service_development

Complete guide for developing services and business logic components in the PySide POEditor Plugin.

.. contents:: Table of Contents
   :local:
   :depth: 3

Overview
========

Services in the PySide POEditor Plugin provide reusable business logic, data processing, and system integration capabilities. This guide covers:

* **Service Architecture**: Understanding the service system
* **Service Patterns**: Common service implementation patterns
* **API Integration**: Integrating services with the plugin API
* **Lifecycle Management**: Service initialization and cleanup
* **Testing**: Testing service functionality

Service System Architecture
===========================

How Services Work
-----------------

Services are modular components that provide specific functionality:

.. code-block:: text

   Service System Architecture:
   ├── Core Services
   │   ├── ThemeManager             # Theme management service
   │   ├── SettingsManager          # Application settings
   │   ├── TabManager               # Tab management
   │   └── SidebarManager           # Sidebar management
   ├── CSS Services
   │   ├── CSSFileBasedThemeManager # CSS theme management
   │   ├── CSSPreprocessor          # CSS processing
   │   ├── IconPreprocessor         # Icon processing
   │   └── AdvancedCSSCache         # CSS caching
   └── Custom Services
       ├── DataService              # Your data service
       ├── NetworkService           # Your network service
       └── ProcessingService        # Your processing service

**Key Characteristics:**

* **Single Responsibility**: Each service has one clear purpose
* **Reusability**: Services can be used across multiple components
* **Testability**: Services are easily unit testable
* **Loose Coupling**: Services communicate through well-defined interfaces

Service Categories
-----------------

**Core Services:**
- System-level functionality (themes, settings, UI management)
- Always available through the application lifecycle

**Feature Services:**
- Specific functionality for features (search, file operations)
- May be loaded on-demand

**Plugin Services:**
- Services specific to individual plugins
- Loaded/unloaded with plugin lifecycle

Creating Custom Services
=======================

Step 1: Service Base Structure
------------------------------

Create a service following the established patterns:

.. code-block:: python

   # services/my_data_service.py
   from typing import Dict, List, Optional, Any
   from PySide6.QtCore import QObject, Signal
   
   from lg import logger
   
   class MyDataService(QObject):
       """Service for handling data operations"""
       
       # Service signals
       data_loaded = Signal(dict)
       data_saved = Signal(str)
       data_error = Signal(str)
       
       def __init__(self, parent=None):
           super().__init__(parent)
           self._data_cache: Dict[str, Any] = {}
           self._is_initialized = False
           logger.info(f"Initializing {self.__class__.__name__}")
       
       def initialize(self) -> bool:
           """Initialize the service"""
           try:
               if self._is_initialized:
                   return True
               
               # Perform initialization tasks
               self._setup_cache()
               self._load_persistent_data()
               
               self._is_initialized = True
               logger.info(f"{self.__class__.__name__} initialized successfully")
               return True
               
           except Exception as e:
               logger.error(f"Failed to initialize {self.__class__.__name__}: {e}")
               return False
       
       def cleanup(self) -> None:
           """Clean up service resources"""
           try:
               if not self._is_initialized:
                   return
               
               # Save any persistent data
               self._save_persistent_data()
               
               # Clear cache
               self._data_cache.clear()
               
               self._is_initialized = False
               logger.info(f"{self.__class__.__name__} cleaned up successfully")
               
           except Exception as e:
               logger.error(f"Error during {self.__class__.__name__} cleanup: {e}")
       
       @property
       def is_initialized(self) -> bool:
           """Check if service is initialized"""
           return self._is_initialized
       
       def _setup_cache(self) -> None:
           """Set up internal cache"""
           self._data_cache = {}
       
       def _load_persistent_data(self) -> None:
           """Load persistent data if available"""
           # Override in subclasses to implement persistence
           pass
       
       def _save_persistent_data(self) -> None:
           """Save persistent data"""
           # Override in subclasses to implement persistence
           pass

Step 2: Implement Service Logic
------------------------------

Add the core service functionality:

.. code-block:: python

   # Continue services/my_data_service.py
   
   class MyDataService(QObject):
       # ... previous code ...
       
       def load_data(self, source_id: str, force_reload: bool = False) -> Optional[Dict]:
           """Load data from source"""
           if not self._is_initialized:
               logger.warning("Service not initialized")
               return None
           
           try:
               # Check cache first
               if source_id in self._data_cache and not force_reload:
                   logger.debug(f"Returning cached data for {source_id}")
                   return self._data_cache[source_id]
               
               # Load data (simulate data loading)
               data = self._fetch_data_from_source(source_id)
               
               # Cache the data
               self._data_cache[source_id] = data
               
               # Emit signal
               self.data_loaded.emit(data)
               
               logger.info(f"Data loaded successfully for {source_id}")
               return data
               
           except Exception as e:
               error_msg = f"Failed to load data for {source_id}: {e}"
               logger.error(error_msg)
               self.data_error.emit(error_msg)
               return None
       
       def save_data(self, source_id: str, data: Dict) -> bool:
           """Save data to source"""
           if not self._is_initialized:
               logger.warning("Service not initialized")
               return False
           
           try:
               # Validate data
               if not self._validate_data(data):
                   raise ValueError("Invalid data format")
               
               # Save data (simulate data saving)
               success = self._write_data_to_source(source_id, data)
               
               if success:
                   # Update cache
                   self._data_cache[source_id] = data
                   
                   # Emit signal
                   self.data_saved.emit(source_id)
                   
                   logger.info(f"Data saved successfully for {source_id}")
                   return True
               else:
                   raise Exception("Failed to write data")
                   
           except Exception as e:
               error_msg = f"Failed to save data for {source_id}: {e}"
               logger.error(error_msg)
               self.data_error.emit(error_msg)
               return False
       
       def get_cached_data(self, source_id: str) -> Optional[Dict]:
           """Get data from cache without loading"""
           return self._data_cache.get(source_id)
       
       def clear_cache(self, source_id: Optional[str] = None) -> None:
           """Clear cache for specific source or all sources"""
           if source_id:
               self._data_cache.pop(source_id, None)
               logger.debug(f"Cache cleared for {source_id}")
           else:
               self._data_cache.clear()
               logger.debug("All cache cleared")
       
       def get_cache_stats(self) -> Dict[str, Any]:
           """Get cache statistics"""
           return {
               "entries": len(self._data_cache),
               "sources": list(self._data_cache.keys()),
               "memory_usage": self._estimate_cache_memory()
           }
       
       # Private helper methods
       def _fetch_data_from_source(self, source_id: str) -> Dict:
           """Fetch data from external source"""
           # Implement actual data fetching logic
           # This is a placeholder implementation
           return {
               "source_id": source_id,
               "items": [f"item_{i}" for i in range(10)],
               "timestamp": self._get_current_timestamp()
           }
       
       def _write_data_to_source(self, source_id: str, data: Dict) -> bool:
           """Write data to external source"""
           # Implement actual data writing logic
           # This is a placeholder implementation
           return True
       
       def _validate_data(self, data: Dict) -> bool:
           """Validate data format"""
           required_keys = ["source_id", "items"]
           return all(key in data for key in required_keys)
       
       def _estimate_cache_memory(self) -> int:
           """Estimate cache memory usage in bytes"""
           import sys
           return sum(sys.getsizeof(item) for item in self._data_cache.values())
       
       def _get_current_timestamp(self) -> str:
           """Get current timestamp"""
           from datetime import datetime
           return datetime.now().isoformat()

Step 3: Asynchronous Service Operations
--------------------------------------

For services that need background processing:

.. code-block:: python

   # services/async_processing_service.py
   from PySide6.QtCore import QObject, Signal, QThread, QTimer
   from typing import Callable, Any
   
   class BackgroundWorker(QObject):
       """Worker for background processing"""
       
       finished = Signal(object)  # Result
       error = Signal(str)        # Error message
       progress = Signal(int)     # Progress percentage
       
       def __init__(self, task_func: Callable, *args, **kwargs):
           super().__init__()
           self.task_func = task_func
           self.args = args
           self.kwargs = kwargs
       
       def run(self):
           """Run the task"""
           try:
               result = self.task_func(*self.args, **self.kwargs)
               self.finished.emit(result)
           except Exception as e:
               self.error.emit(str(e))
   
   class AsyncProcessingService(QObject):
       """Service for asynchronous processing operations"""
       
       task_completed = Signal(str, object)  # task_id, result
       task_failed = Signal(str, str)        # task_id, error
       task_progress = Signal(str, int)      # task_id, progress
       
       def __init__(self, parent=None):
           super().__init__(parent)
           self._active_tasks = {}
           self._task_counter = 0
       
       def start_task(self, task_func: Callable, *args, **kwargs) -> str:
           """Start a background task"""
           task_id = f"task_{self._task_counter}"
           self._task_counter += 1
           
           # Create worker and thread
           worker = BackgroundWorker(task_func, *args, **kwargs)
           thread = QThread()
           
           # Move worker to thread
           worker.moveToThread(thread)
           
           # Connect signals
           thread.started.connect(worker.run)
           worker.finished.connect(lambda result: self._on_task_completed(task_id, result))
           worker.error.connect(lambda error: self._on_task_failed(task_id, error))
           worker.progress.connect(lambda progress: self._on_task_progress(task_id, progress))
           
           # Store task info
           self._active_tasks[task_id] = {
               'worker': worker,
               'thread': thread
           }
           
           # Start thread
           thread.start()
           
           logger.info(f"Started background task: {task_id}")
           return task_id
       
       def cancel_task(self, task_id: str) -> bool:
           """Cancel a running task"""
           if task_id not in self._active_tasks:
               return False
           
           task_info = self._active_tasks[task_id]
           thread = task_info['thread']
           
           if thread.isRunning():
               thread.quit()
               thread.wait(5000)  # Wait up to 5 seconds
           
           del self._active_tasks[task_id]
           logger.info(f"Cancelled task: {task_id}")
           return True
       
       def get_active_tasks(self) -> List[str]:
           """Get list of active task IDs"""
           return list(self._active_tasks.keys())
       
       def _on_task_completed(self, task_id: str, result: Any):
           """Handle task completion"""
           if task_id in self._active_tasks:
               self._cleanup_task(task_id)
               self.task_completed.emit(task_id, result)
               logger.info(f"Task completed: {task_id}")
       
       def _on_task_failed(self, task_id: str, error: str):
           """Handle task failure"""
           if task_id in self._active_tasks:
               self._cleanup_task(task_id)
               self.task_failed.emit(task_id, error)
               logger.error(f"Task failed: {task_id} - {error}")
       
       def _on_task_progress(self, task_id: str, progress: int):
           """Handle task progress update"""
           self.task_progress.emit(task_id, progress)
       
       def _cleanup_task(self, task_id: str):
           """Clean up completed task"""
           if task_id in self._active_tasks:
               task_info = self._active_tasks[task_id]
               thread = task_info['thread']
               
               if thread.isRunning():
                   thread.quit()
                   thread.wait()
               
               del self._active_tasks[task_id]

Step 4: Service Configuration
-----------------------------

Create configurable services:

.. code-block:: python

   # services/configurable_service.py
   from typing import Dict, Any
   from PySide6.QtCore import QObject
   
   class ConfigurableService(QObject):
       """Base class for services with configuration"""
       
       def __init__(self, config: Optional[Dict[str, Any]] = None, parent=None):
           super().__init__(parent)
           self._config = config or self._get_default_config()
           self._validate_config()
       
       def _get_default_config(self) -> Dict[str, Any]:
           """Get default configuration"""
           return {
               "enabled": True,
               "cache_size": 100,
               "timeout": 5000,
               "retry_count": 3
           }
       
       def _validate_config(self) -> None:
           """Validate configuration"""
           required_keys = ["enabled", "cache_size", "timeout"]
           for key in required_keys:
               if key not in self._config:
                   raise ValueError(f"Missing required config key: {key}")
       
       def update_config(self, new_config: Dict[str, Any]) -> None:
           """Update service configuration"""
           self._config.update(new_config)
           self._validate_config()
           self._apply_config_changes()
       
       def get_config(self) -> Dict[str, Any]:
           """Get current configuration"""
           return self._config.copy()
       
       def _apply_config_changes(self) -> None:
           """Apply configuration changes"""
           # Override in subclasses
           pass

Service Integration Patterns
===========================

Plugin API Integration
---------------------

Integrate services with the Plugin API:

.. code-block:: python

   # core/api.py - Add service to API
   class PluginAPI:
       def __init__(self, **kwargs):
           # Existing services
           self.activity_manager = kwargs.get('activity_manager')
           self.theme_manager = kwargs.get('theme_manager')
           
           # Add custom services
           self.data_service = kwargs.get('data_service')
           self.processing_service = kwargs.get('processing_service')

.. code-block:: python

   # Usage in plugins
   class MyPlugin:
       def __init__(self, api: PluginAPI):
           self.api = api
       
       def use_services(self):
           """Use API services"""
           # Use data service
           if hasattr(self.api, 'data_service'):
               data = self.api.data_service.load_data('my_source')
           
           # Use processing service
           if hasattr(self.api, 'processing_service'):
               task_id = self.api.processing_service.start_task(self.process_function)

Service Factory Pattern
----------------------

Create services using factory pattern:

.. code-block:: python

   # services/service_factory.py
   from typing import Type, Dict, Any
   
   class ServiceFactory:
       """Factory for creating service instances"""
       
       _service_registry: Dict[str, Type] = {}
       
       @classmethod
       def register_service(cls, name: str, service_class: Type) -> None:
           """Register a service class"""
           cls._service_registry[name] = service_class
       
       @classmethod
       def create_service(cls, name: str, config: Dict[str, Any] = None, **kwargs) -> Any:
           """Create a service instance"""
           if name not in cls._service_registry:
               raise ValueError(f"Unknown service: {name}")
           
           service_class = cls._service_registry[name]
           return service_class(config=config, **kwargs)
       
       @classmethod
       def get_available_services(cls) -> List[str]:
           """Get list of available services"""
           return list(cls._service_registry.keys())
   
   # Register services
   ServiceFactory.register_service('data', MyDataService)
   ServiceFactory.register_service('processing', AsyncProcessingService)
   
   # Create services
   data_service = ServiceFactory.create_service('data', config={'cache_size': 200})
   processing_service = ServiceFactory.create_service('processing')

Dependency Injection
-------------------

Implement dependency injection for services:

.. code-block:: python

   # services/service_container.py
   from typing import Dict, Any, Callable
   
   class ServiceContainer:
       """Container for managing service dependencies"""
       
       def __init__(self):
           self._services: Dict[str, Any] = {}
           self._factories: Dict[str, Callable] = {}
           self._singletons: Dict[str, Any] = {}
       
       def register(self, name: str, factory: Callable) -> None:
           """Register a service factory"""
           self._factories[name] = factory
       
       def register_singleton(self, name: str, factory: Callable) -> None:
           """Register a singleton service"""
           self._factories[name] = factory
           self._singletons[name] = None
       
       def get(self, name: str) -> Any:
           """Get a service instance"""
           if name in self._singletons:
               if self._singletons[name] is None:
                   self._singletons[name] = self._factories[name]()
               return self._singletons[name]
           
           if name in self._factories:
               return self._factories[name]()
           
           raise ValueError(f"Service not found: {name}")
       
       def has(self, name: str) -> bool:
           """Check if service is registered"""
           return name in self._factories
   
   # Usage
   container = ServiceContainer()
   
   # Register services
   container.register_singleton('data_service', lambda: MyDataService())
   container.register('processing_service', lambda: AsyncProcessingService())
   
   # Get services
   data_service = container.get('data_service')
   processing_service = container.get('processing_service')

Service Communication
====================

Event-Driven Communication
--------------------------

Use signals for service communication:

.. code-block:: python

   # services/event_bus.py
   from PySide6.QtCore import QObject, Signal
   from typing import Dict, List, Callable
   
   class EventBus(QObject):
       """Central event bus for service communication"""
       
       # Generic event signal
       event_emitted = Signal(str, dict)  # event_name, event_data
       
       def __init__(self, parent=None):
           super().__init__(parent)
           self._listeners: Dict[str, List[Callable]] = {}
       
       def subscribe(self, event_name: str, callback: Callable) -> None:
           """Subscribe to an event"""
           if event_name not in self._listeners:
               self._listeners[event_name] = []
           self._listeners[event_name].append(callback)
       
       def unsubscribe(self, event_name: str, callback: Callable) -> None:
           """Unsubscribe from an event"""
           if event_name in self._listeners:
               if callback in self._listeners[event_name]:
                   self._listeners[event_name].remove(callback)
       
       def emit_event(self, event_name: str, event_data: Dict = None) -> None:
           """Emit an event"""
           event_data = event_data or {}
           
           # Emit Qt signal
           self.event_emitted.emit(event_name, event_data)
           
           # Call direct listeners
           if event_name in self._listeners:
               for callback in self._listeners[event_name]:
                   try:
                       callback(event_data)
                   except Exception as e:
                       logger.error(f"Error in event listener: {e}")

Service Orchestration
--------------------

Coordinate multiple services:

.. code-block:: python

   # services/service_orchestrator.py
   class ServiceOrchestrator(QObject):
       """Orchestrates multiple services"""
       
       def __init__(self, services: Dict[str, Any], parent=None):
           super().__init__(parent)
           self.services = services
           self._initialization_order = []
       
       def initialize_all(self) -> bool:
           """Initialize all services in proper order"""
           try:
               for service_name in self._initialization_order:
                   if service_name in self.services:
                       service = self.services[service_name]
                       if hasattr(service, 'initialize'):
                           if not service.initialize():
                               logger.error(f"Failed to initialize {service_name}")
                               return False
                       logger.info(f"Initialized service: {service_name}")
               return True
           except Exception as e:
               logger.error(f"Service initialization failed: {e}")
               return False
       
       def cleanup_all(self) -> None:
           """Clean up all services"""
           # Clean up in reverse order
           for service_name in reversed(self._initialization_order):
               if service_name in self.services:
                   service = self.services[service_name]
                   if hasattr(service, 'cleanup'):
                       try:
                           service.cleanup()
                           logger.info(f"Cleaned up service: {service_name}")
                       except Exception as e:
                           logger.error(f"Error cleaning up {service_name}: {e}")
       
       def set_initialization_order(self, order: List[str]) -> None:
           """Set service initialization order"""
           self._initialization_order = order

Service Testing
==============

Unit Testing Services
--------------------

Create comprehensive unit tests:

.. code-block:: python

   # tests/services/test_my_data_service.py
   import unittest
   from unittest.mock import Mock, patch
   
   from services.my_data_service import MyDataService
   
   class TestMyDataService(unittest.TestCase):
       def setUp(self):
           """Set up test environment"""
           self.service = MyDataService()
           self.service.initialize()
       
       def tearDown(self):
           """Clean up after tests"""
           self.service.cleanup()
       
       def test_service_initialization(self):
           """Test service initialization"""
           service = MyDataService()
           self.assertFalse(service.is_initialized)
           
           result = service.initialize()
           self.assertTrue(result)
           self.assertTrue(service.is_initialized)
       
       def test_load_data_success(self):
           """Test successful data loading"""
           with patch.object(self.service, '_fetch_data_from_source') as mock_fetch:
               mock_data = {"test": "data"}
               mock_fetch.return_value = mock_data
               
               result = self.service.load_data("test_source")
               
               self.assertEqual(result, mock_data)
               mock_fetch.assert_called_once_with("test_source")
       
       def test_load_data_caching(self):
           """Test data caching functionality"""
           with patch.object(self.service, '_fetch_data_from_source') as mock_fetch:
               mock_data = {"test": "data"}
               mock_fetch.return_value = mock_data
               
               # First call should fetch data
               result1 = self.service.load_data("test_source")
               self.assertEqual(mock_fetch.call_count, 1)
               
               # Second call should use cache
               result2 = self.service.load_data("test_source")
               self.assertEqual(mock_fetch.call_count, 1)  # Still 1
               self.assertEqual(result1, result2)
       
       def test_save_data_success(self):
           """Test successful data saving"""
           with patch.object(self.service, '_write_data_to_source') as mock_write:
               mock_write.return_value = True
               
               test_data = {"source_id": "test", "items": ["item1", "item2"]}
               result = self.service.save_data("test_source", test_data)
               
               self.assertTrue(result)
               mock_write.assert_called_once_with("test_source", test_data)
       
       def test_cache_statistics(self):
           """Test cache statistics"""
           # Load some test data
           self.service._data_cache["test1"] = {"data": "value1"}
           self.service._data_cache["test2"] = {"data": "value2"}
           
           stats = self.service.get_cache_stats()
           
           self.assertEqual(stats["entries"], 2)
           self.assertIn("test1", stats["sources"])
           self.assertIn("test2", stats["sources"])
           self.assertGreater(stats["memory_usage"], 0)

Integration Testing
------------------

Test service integration:

.. code-block:: python

   # tests/integration/test_service_integration.py
   import unittest
   from PySide6.QtWidgets import QApplication
   from PySide6.QtCore import QSignalSpy
   
   from services.my_data_service import MyDataService
   from services.async_processing_service import AsyncProcessingService
   
   class TestServiceIntegration(unittest.TestCase):
       @classmethod
       def setUpClass(cls):
           """Set up test application"""
           cls.app = QApplication.instance() or QApplication([])
       
       def setUp(self):
           """Set up test services"""
           self.data_service = MyDataService()
           self.processing_service = AsyncProcessingService()
           
           self.data_service.initialize()
       
       def tearDown(self):
           """Clean up test services"""
           self.data_service.cleanup()
       
       def test_service_communication(self):
           """Test communication between services"""
           # Set up signal spy
           spy = QSignalSpy(self.data_service.data_loaded)
           
           # Load data
           result = self.data_service.load_data("test_source")
           
           # Verify signal was emitted
           self.assertEqual(len(spy), 1)
           self.assertIsNotNone(result)
       
       def test_async_processing_integration(self):
           """Test async processing service integration"""
           def test_task():
               return {"result": "processed"}
           
           # Start async task
           task_id = self.processing_service.start_task(test_task)
           
           # Verify task was started
           self.assertIn(task_id, self.processing_service.get_active_tasks())

Performance Testing
------------------

Test service performance:

.. code-block:: python

   # tests/performance/test_service_performance.py
   import unittest
   import time
   from services.my_data_service import MyDataService
   
   class TestServicePerformance(unittest.TestCase):
       def setUp(self):
           """Set up performance test environment"""
           self.service = MyDataService()
           self.service.initialize()
       
       def test_load_performance(self):
           """Test data loading performance"""
           # Warm up
           self.service.load_data("warmup")
           
           # Measure performance
           start_time = time.perf_counter()
           
           for i in range(100):
               self.service.load_data(f"source_{i}")
           
           end_time = time.perf_counter()
           total_time = end_time - start_time
           
           # Assert performance requirements
           self.assertLess(total_time, 1.0)  # Should complete in under 1 second
           
           avg_time = total_time / 100
           self.assertLess(avg_time, 0.01)  # Average under 10ms per operation
       
       def test_cache_performance(self):
           """Test cache performance"""
           # Load initial data
           self.service.load_data("cached_source")
           
           # Measure cached access performance
           start_time = time.perf_counter()
           
           for i in range(1000):
               self.service.get_cached_data("cached_source")
           
           end_time = time.perf_counter()
           total_time = end_time - start_time
           
           # Cache access should be very fast
           self.assertLess(total_time, 0.1)  # Should complete in under 100ms

Best Practices
=============

Service Design Guidelines
------------------------

1. **Single Responsibility**: Each service should have one clear purpose
2. **Dependency Injection**: Use dependency injection for better testability
3. **Interface Segregation**: Create specific interfaces for different service aspects
4. **Error Handling**: Implement comprehensive error handling and logging
5. **Resource Management**: Properly manage resources and clean up

Implementation Patterns
----------------------

1. **Initialization Pattern**: Always implement initialize() and cleanup() methods
2. **Signal Communication**: Use Qt signals for loose coupling between services
3. **Configuration Management**: Make services configurable when appropriate
4. **Caching Strategy**: Implement appropriate caching for performance
5. **Async Operations**: Use background threads for long-running operations

Code Organization
----------------

1. **Service Directory**: Keep all services in the services/ directory
2. **Clear Naming**: Use descriptive names that indicate service purpose
3. **Documentation**: Document all public methods and service capabilities
4. **Version Control**: Include version information for service APIs
5. **Testing**: Maintain comprehensive test coverage

Summary
======

Creating services for the PySide POEditor Plugin involves:

1. **Service Structure**: Create services with clear initialization and cleanup
2. **Business Logic**: Implement core functionality with proper error handling
3. **Configuration**: Make services configurable when appropriate
4. **Integration**: Integrate with Plugin API and other services
5. **Communication**: Use signals for service communication
6. **Testing**: Create comprehensive unit and integration tests
7. **Performance**: Optimize for performance and resource usage

**Key Points:**

* Follow established service patterns and interfaces
* Use dependency injection for better testability
* Implement proper resource management
* Use signals for loose coupling
* Create comprehensive tests
* Document service APIs clearly

For additional information, see:

* :doc:`plugin_development_guide` - Creating plugins that use services
* :doc:`panel_development_guide` - UI panels that integrate with services
* :doc:`manager_development_guide` - Creating service managers
* :doc:`/services/index` - Service API reference
