==============================
Manager Development Guide
==============================

.. py:module:: guides.manager_development

Complete guide for developing managers and core system components in the PySide POEditor Plugin.

.. contents:: Table of Contents
   :local:
   :depth: 3

Overview
========

Managers are core system components that coordinate between different parts of the application. This guide covers:

* **Manager Architecture**: Understanding manager responsibilities
* **Manager Patterns**: Common implementation patterns
* **System Integration**: Coordinating with other managers
* **Lifecycle Management**: Initialization and cleanup
* **Best Practices**: Performance and maintainability

Manager System Architecture
===========================

How Managers Work
------------------

Managers coordinate system-level functionality:

.. code-block:: text

   Manager System Architecture:
   ├── Core Managers
   │   ├── ActivityManager           # Activity bar coordination
   │   ├── SidebarManager            # Sidebar and panel management
   │   ├── TabManager                # Tab management
   │   ├── PluginManager             # Plugin lifecycle
   │   ├── SettingsManager           # Application settings
   │   └── ThemeManager              # Theme coordination
   ├── CSS Managers
   │   └── CSSFileBasedThemeManager  # CSS theme management
   └── Custom Managers
       ├── DataManager               # Your data management
       ├── NetworkManager            # Network coordination
       └── CacheManager              # Cache management

**Key Responsibilities:**

* **Coordination**: Manage interactions between components
* **Lifecycle**: Handle initialization and cleanup
* **State Management**: Maintain system state
* **Event Coordination**: Coordinate system-wide events

Manager Categories
-------------------

**Core Managers:**
- System-level coordination (UI, plugins, settings)
- Always active during application lifecycle

**Feature Managers:**
- Specific functionality coordination (data, network, cache)
- May be loaded on-demand

**Plugin Managers:**
- Manager-like components within plugins
- Loaded/unloaded with plugin lifecycle

Creating Custom Managers
========================

Step 1: Manager Base Structure
------------------------------

Create a manager following established patterns:

.. code-block:: python

   # managers/my_data_manager.py
   from typing import Dict, List, Optional, Any
   from PySide6.QtCore import QObject, Signal
   
   from lg import logger
   
   class MyDataManager(QObject):
       """Manager for coordinating data operations across the application"""
       
       # Manager signals
       data_source_added = Signal(str)      # source_id
       data_source_removed = Signal(str)    # source_id
       data_updated = Signal(str, dict)     # source_id, data
       manager_ready = Signal()
       manager_error = Signal(str)
       
       def __init__(self, parent=None):
           super().__init__(parent)
           self._data_sources: Dict[str, Any] = {}
           self._data_services: Dict[str, Any] = {}
           self._is_initialized = False
           self._active_operations: Dict[str, Any] = {}
           
           logger.info(f"Initializing {self.__class__.__name__}")
       
       def initialize(self) -> bool:
           """Initialize the manager"""
           try:
               if self._is_initialized:
                   return True
               
               # Initialize internal systems
               self._setup_data_sources()
               self._setup_data_services()
               self._connect_service_signals()
               
               self._is_initialized = True
               self.manager_ready.emit()
               logger.info(f"{self.__class__.__name__} initialized successfully")
               return True
               
           except Exception as e:
               error_msg = f"Failed to initialize {self.__class__.__name__}: {e}"
               logger.error(error_msg)
               self.manager_error.emit(error_msg)
               return False
       
       def cleanup(self) -> None:
           """Clean up manager resources"""
           try:
               if not self._is_initialized:
                   return
               
               # Stop active operations
               self._stop_active_operations()
               
               # Cleanup services
               self._cleanup_data_services()
               
               # Clear data sources
               self._data_sources.clear()
               
               self._is_initialized = False
               logger.info(f"{self.__class__.__name__} cleaned up successfully")
               
           except Exception as e:
               logger.error(f"Error during {self.__class__.__name__} cleanup: {e}")
       
       @property
       def is_initialized(self) -> bool:
           """Check if manager is initialized"""
           return self._is_initialized
       
       def _setup_data_sources(self) -> None:
           """Set up data source registry"""
           self._data_sources = {}
       
       def _setup_data_services(self) -> None:
           """Set up data services"""
           # Initialize services that this manager coordinates
           pass
       
       def _connect_service_signals(self) -> None:
           """Connect to service signals"""
           # Connect to relevant service signals for coordination
           pass
       
       def _stop_active_operations(self) -> None:
           """Stop any active operations"""
           for operation_id, operation in self._active_operations.items():
               try:
                   if hasattr(operation, 'stop'):
                       operation.stop()
                   logger.info(f"Stopped operation: {operation_id}")
               except Exception as e:
                   logger.error(f"Error stopping operation {operation_id}: {e}")
           
           self._active_operations.clear()
       
       def _cleanup_data_services(self) -> None:
           """Clean up data services"""
           for service_id, service in self._data_services.items():
               try:
                   if hasattr(service, 'cleanup'):
                       service.cleanup()
                   logger.info(f"Cleaned up service: {service_id}")
               except Exception as e:
                   logger.error(f"Error cleaning up service {service_id}: {e}")

Step 2: Manager Core Functionality
----------------------------------

Implement the manager's coordination logic:

.. code-block:: python

   # Continue managers/my_data_manager.py
   
   class MyDataManager(QObject):
       # ... previous code ...
       
       def register_data_source(self, source_id: str, source_config: Dict[str, Any]) -> bool:
           """Register a new data source"""
           if not self._is_initialized:
               logger.warning("Manager not initialized")
               return False
           
           try:
               if source_id in self._data_sources:
                   logger.warning(f"Data source already registered: {source_id}")
                   return False
               
               # Validate source configuration
               if not self._validate_source_config(source_config):
                   raise ValueError("Invalid source configuration")
               
               # Register the source
               self._data_sources[source_id] = {
                   'config': source_config,
                   'status': 'registered',
                   'last_update': None
               }
               
               self.data_source_added.emit(source_id)
               logger.info(f"Registered data source: {source_id}")
               return True
               
           except Exception as e:
               logger.error(f"Failed to register data source {source_id}: {e}")
               return False
       
       def unregister_data_source(self, source_id: str) -> bool:
           """Unregister a data source"""
           if not self._is_initialized:
               logger.warning("Manager not initialized")
               return False
           
           try:
               if source_id not in self._data_sources:
                   logger.warning(f"Data source not found: {source_id}")
                   return False
               
               # Stop any operations for this source
               self._stop_source_operations(source_id)
               
               # Remove the source
               del self._data_sources[source_id]
               
               self.data_source_removed.emit(source_id)
               logger.info(f"Unregistered data source: {source_id}")
               return True
               
           except Exception as e:
               logger.error(f"Failed to unregister data source {source_id}: {e}")
               return False
       
       def get_data_sources(self) -> List[str]:
           """Get list of registered data sources"""
           return list(self._data_sources.keys())
       
       def get_source_status(self, source_id: str) -> Optional[str]:
           """Get status of a data source"""
           source = self._data_sources.get(source_id)
           return source.get('status') if source else None
       
       def coordinate_data_operation(self, operation_type: str, source_id: str, 
                                   operation_data: Dict[str, Any]) -> Optional[str]:
           """Coordinate a data operation across services"""
           if not self._is_initialized:
               logger.warning("Manager not initialized")
               return None
           
           try:
               if source_id not in self._data_sources:
                   raise ValueError(f"Unknown data source: {source_id}")
               
               # Generate operation ID
               operation_id = f"{operation_type}_{source_id}_{len(self._active_operations)}"
               
               # Create operation context
               operation = {
                   'id': operation_id,
                   'type': operation_type,
                   'source_id': source_id,
                   'data': operation_data,
                   'status': 'active',
                   'services': []
               }
               
               # Coordinate with relevant services
               self._coordinate_with_services(operation)
               
               # Track the operation
               self._active_operations[operation_id] = operation
               
               logger.info(f"Started coordinated operation: {operation_id}")
               return operation_id
               
           except Exception as e:
               logger.error(f"Failed to coordinate operation for {source_id}: {e}")
               return None
       
       def get_operation_status(self, operation_id: str) -> Optional[str]:
           """Get status of an active operation"""
           operation = self._active_operations.get(operation_id)
           return operation.get('status') if operation else None
       
       def cancel_operation(self, operation_id: str) -> bool:
           """Cancel an active operation"""
           if operation_id not in self._active_operations:
               return False
           
           try:
               operation = self._active_operations[operation_id]
               
               # Cancel operation in all involved services
               for service in operation.get('services', []):
                   if hasattr(service, 'cancel_operation'):
                       service.cancel_operation(operation_id)
               
               # Remove from active operations
               del self._active_operations[operation_id]
               
               logger.info(f"Cancelled operation: {operation_id}")
               return True
               
           except Exception as e:
               logger.error(f"Error cancelling operation {operation_id}: {e}")
               return False
       
       # Private helper methods
       def _validate_source_config(self, config: Dict[str, Any]) -> bool:
           """Validate source configuration"""
           required_keys = ['type', 'name']
           return all(key in config for key in required_keys)
       
       def _stop_source_operations(self, source_id: str) -> None:
           """Stop all operations for a specific source"""
           operations_to_stop = [
               op_id for op_id, op in self._active_operations.items()
               if op.get('source_id') == source_id
           ]
           
           for op_id in operations_to_stop:
               self.cancel_operation(op_id)
       
       def _coordinate_with_services(self, operation: Dict[str, Any]) -> None:
           """Coordinate operation with relevant services"""
           # Determine which services are needed for this operation
           # This would be specific to your application logic
           pass

Step 3: Manager Event Coordination
----------------------------------

Implement event coordination between components:

.. code-block:: python

   # managers/event_coordination_manager.py
   from PySide6.QtCore import QObject, Signal, QTimer
   from typing import Dict, List, Callable
   
   class EventCoordinationManager(QObject):
       """Manager for coordinating events across the application"""
       
       # Coordination signals
       system_event = Signal(str, dict)           # event_type, event_data
       component_registered = Signal(str)         # component_id
       component_unregistered = Signal(str)       # component_id
       
       def __init__(self, parent=None):
           super().__init__(parent)
           self._registered_components: Dict[str, Any] = {}
           self._event_handlers: Dict[str, List[Callable]] = {}
           self._event_queue: List[Dict[str, Any]] = []
           self._processing_timer = QTimer()
           
           self._setup_event_processing()
       
       def _setup_event_processing(self):
           """Set up event processing timer"""
           self._processing_timer.timeout.connect(self._process_event_queue)
           self._processing_timer.start(100)  # Process every 100ms
       
       def register_component(self, component_id: str, component: Any, 
                            event_handlers: Dict[str, Callable] = None) -> bool:
           """Register a component for event coordination"""
           try:
               if component_id in self._registered_components:
                   logger.warning(f"Component already registered: {component_id}")
                   return False
               
               # Register component
               self._registered_components[component_id] = {
                   'component': component,
                   'handlers': event_handlers or {},
                   'status': 'active'
               }
               
               # Register event handlers
               if event_handlers:
                   for event_type, handler in event_handlers.items():
                       self._register_event_handler(event_type, handler)
               
               self.component_registered.emit(component_id)
               logger.info(f"Registered component: {component_id}")
               return True
               
           except Exception as e:
               logger.error(f"Failed to register component {component_id}: {e}")
               return False
       
       def unregister_component(self, component_id: str) -> bool:
           """Unregister a component"""
           try:
               if component_id not in self._registered_components:
                   return False
               
               # Remove event handlers
               component_info = self._registered_components[component_id]
               for event_type, handler in component_info.get('handlers', {}).items():
                   self._unregister_event_handler(event_type, handler)
               
               # Remove component
               del self._registered_components[component_id]
               
               self.component_unregistered.emit(component_id)
               logger.info(f"Unregistered component: {component_id}")
               return True
               
           except Exception as e:
               logger.error(f"Error unregistering component {component_id}: {e}")
               return False
       
       def emit_coordinated_event(self, event_type: str, event_data: Dict[str, Any] = None,
                                priority: int = 0) -> None:
           """Emit an event for coordination"""
           event = {
               'type': event_type,
               'data': event_data or {},
               'priority': priority,
               'timestamp': self._get_timestamp()
           }
           
           # Add to event queue
           self._event_queue.append(event)
           
           # Sort queue by priority (higher priority first)
           self._event_queue.sort(key=lambda x: x['priority'], reverse=True)
       
       def _process_event_queue(self):
           """Process queued events"""
           if not self._event_queue:
               return
           
           # Process one event per timer tick to avoid blocking
           event = self._event_queue.pop(0)
           self._process_single_event(event)
       
       def _process_single_event(self, event: Dict[str, Any]):
           """Process a single event"""
           try:
               event_type = event['type']
               event_data = event['data']
               
               # Emit system signal
               self.system_event.emit(event_type, event_data)
               
               # Call registered handlers
               handlers = self._event_handlers.get(event_type, [])
               for handler in handlers:
                   try:
                       handler(event_data)
                   except Exception as e:
                       logger.error(f"Error in event handler: {e}")
               
               logger.debug(f"Processed event: {event_type}")
               
           except Exception as e:
               logger.error(f"Error processing event: {e}")
       
       def _register_event_handler(self, event_type: str, handler: Callable):
           """Register an event handler"""
           if event_type not in self._event_handlers:
               self._event_handlers[event_type] = []
           self._event_handlers[event_type].append(handler)
       
       def _unregister_event_handler(self, event_type: str, handler: Callable):
           """Unregister an event handler"""
           if event_type in self._event_handlers:
               if handler in self._event_handlers[event_type]:
                   self._event_handlers[event_type].remove(handler)
       
       def _get_timestamp(self) -> str:
           """Get current timestamp"""
           from datetime import datetime
           return datetime.now().isoformat()

Manager Integration Patterns
============================

Manager Factory Pattern
------------------------

Create managers using factory pattern:

.. code-block:: python

   # managers/manager_factory.py
   from typing import Type, Dict, Any
   
   class ManagerFactory:
       """Factory for creating manager instances"""
       
       _manager_registry: Dict[str, Type] = {}
       
       @classmethod
       def register_manager(cls, name: str, manager_class: Type) -> None:
           """Register a manager class"""
           cls._manager_registry[name] = manager_class
       
       @classmethod
       def create_manager(cls, name: str, config: Dict[str, Any] = None, **kwargs) -> Any:
           """Create a manager instance"""
           if name not in cls._manager_registry:
               raise ValueError(f"Unknown manager: {name}")
           
           manager_class = cls._manager_registry[name]
           return manager_class(config=config, **kwargs)
       
       @classmethod
       def get_available_managers(cls) -> List[str]:
           """Get list of available managers"""
           return list(cls._manager_registry.keys())
   
   # Register managers
   ManagerFactory.register_manager('data', MyDataManager)
   ManagerFactory.register_manager('events', EventCoordinationManager)

Manager Orchestration
----------------------

Coordinate multiple managers:

.. code-block:: python

   # core/manager_orchestrator.py
   class ManagerOrchestrator(QObject):
       """Orchestrates multiple managers"""
       
       def __init__(self, parent=None):
           super().__init__(parent)
           self.managers: Dict[str, Any] = {}
           self._initialization_order = []
           self._dependencies: Dict[str, List[str]] = {}
       
       def add_manager(self, name: str, manager: Any, dependencies: List[str] = None) -> None:
           """Add a manager with its dependencies"""
           self.managers[name] = manager
           self._dependencies[name] = dependencies or []
       
       def initialize_all(self) -> bool:
           """Initialize all managers in dependency order"""
           try:
               # Calculate initialization order based on dependencies
               self._calculate_initialization_order()
               
               for manager_name in self._initialization_order:
                   manager = self.managers[manager_name]
                   if hasattr(manager, 'initialize'):
                       if not manager.initialize():
                           logger.error(f"Failed to initialize manager: {manager_name}")
                           return False
                   logger.info(f"Initialized manager: {manager_name}")
               
               return True
               
           except Exception as e:
               logger.error(f"Manager initialization failed: {e}")
               return False
       
       def cleanup_all(self) -> None:
           """Clean up all managers in reverse order"""
           for manager_name in reversed(self._initialization_order):
               manager = self.managers[manager_name]
               if hasattr(manager, 'cleanup'):
                   try:
                       manager.cleanup()
                       logger.info(f"Cleaned up manager: {manager_name}")
                   except Exception as e:
                       logger.error(f"Error cleaning up manager {manager_name}: {e}")
       
       def _calculate_initialization_order(self) -> None:
           """Calculate initialization order based on dependencies"""
           # Simple topological sort
           visited = set()
           temp_visited = set()
           order = []
           
           def visit(manager_name: str):
               if manager_name in temp_visited:
                   raise ValueError(f"Circular dependency detected: {manager_name}")
               if manager_name in visited:
                   return
               
               temp_visited.add(manager_name)
               
               for dependency in self._dependencies.get(manager_name, []):
                   visit(dependency)
               
               temp_visited.remove(manager_name)
               visited.add(manager_name)
               order.append(manager_name)
           
           for manager_name in self.managers:
               if manager_name not in visited:
                   visit(manager_name)
           
           self._initialization_order = order

Manager Testing
================

Unit Testing Managers
----------------------

Create comprehensive manager tests:

.. code-block:: python

   # tests/managers/test_my_data_manager.py
   import unittest
   from unittest.mock import Mock, patch
   from PySide6.QtCore import QSignalSpy
   
   from managers.my_data_manager import MyDataManager
   
   class TestMyDataManager(unittest.TestCase):
       def setUp(self):
           """Set up test environment"""
           self.manager = MyDataManager()
           self.manager.initialize()
       
       def tearDown(self):
           """Clean up after tests"""
           self.manager.cleanup()
       
       def test_manager_initialization(self):
           """Test manager initialization"""
           manager = MyDataManager()
           self.assertFalse(manager.is_initialized)
           
           result = manager.initialize()
           self.assertTrue(result)
           self.assertTrue(manager.is_initialized)
       
       def test_data_source_registration(self):
           """Test data source registration"""
           spy = QSignalSpy(self.manager.data_source_added)
           
           config = {'type': 'test', 'name': 'Test Source'}
           result = self.manager.register_data_source('test_source', config)
           
           self.assertTrue(result)
           self.assertEqual(len(spy), 1)
           self.assertIn('test_source', self.manager.get_data_sources())
       
       def test_operation_coordination(self):
           """Test operation coordination"""
           # Register a data source first
           config = {'type': 'test', 'name': 'Test Source'}
           self.manager.register_data_source('test_source', config)
           
           # Start coordinated operation
           operation_data = {'action': 'load', 'params': {}}
           operation_id = self.manager.coordinate_data_operation(
               'load', 'test_source', operation_data
           )
           
           self.assertIsNotNone(operation_id)
           self.assertEqual(self.manager.get_operation_status(operation_id), 'active')

Integration Testing
--------------------

Test manager integration:

.. code-block:: python

   # tests/integration/test_manager_integration.py
   import unittest
   from PySide6.QtWidgets import QApplication
   
   from core.manager_orchestrator import ManagerOrchestrator
   from managers.my_data_manager import MyDataManager
   from managers.event_coordination_manager import EventCoordinationManager
   
   class TestManagerIntegration(unittest.TestCase):
       @classmethod
       def setUpClass(cls):
           cls.app = QApplication.instance() or QApplication([])
       
       def setUp(self):
           """Set up test environment"""
           self.orchestrator = ManagerOrchestrator()
           
           # Add managers with dependencies
           self.orchestrator.add_manager('events', EventCoordinationManager())
           self.orchestrator.add_manager('data', MyDataManager(), ['events'])
       
       def test_manager_orchestration(self):
           """Test manager orchestration"""
           # Initialize all managers
           result = self.orchestrator.initialize_all()
           self.assertTrue(result)
           
           # Verify managers are initialized
           for manager in self.orchestrator.managers.values():
               if hasattr(manager, 'is_initialized'):
                   self.assertTrue(manager.is_initialized)
           
           # Clean up
           self.orchestrator.cleanup_all()

Best Practices
===============

Manager Design Guidelines
--------------------------

1. **Clear Responsibility**: Each manager should have a clearly defined coordination role
2. **Loose Coupling**: Managers should communicate through well-defined interfaces
3. **Event-Driven**: Use events for coordination rather than direct coupling
4. **Resource Management**: Properly manage resources and dependencies
5. **Error Recovery**: Implement robust error handling and recovery

Implementation Patterns
------------------------

1. **Initialization Order**: Handle dependency-based initialization
2. **Signal Coordination**: Use Qt signals for component coordination
3. **State Management**: Maintain system state consistently
4. **Operation Tracking**: Track long-running operations
5. **Cleanup Procedures**: Implement comprehensive cleanup

Code Organization
------------------

1. **Manager Directory**: Keep all managers in the managers/ directory
2. **Clear Interfaces**: Define clear interfaces for manager communication
3. **Documentation**: Document manager responsibilities and interfaces
4. **Testing**: Maintain comprehensive test coverage
5. **Performance**: Optimize for coordination efficiency

Summary
========

Creating managers for the PySide POEditor Plugin involves:

1. **Coordination Logic**: Implement component coordination and state management
2. **Event System**: Use signals for loose coupling between components
3. **Lifecycle Management**: Handle proper initialization and cleanup
4. **Dependency Management**: Handle manager dependencies correctly
5. **Operation Coordination**: Coordinate complex operations across services
6. **Testing**: Create comprehensive unit and integration tests
7. **Performance**: Optimize for coordination efficiency

**Key Points:**

* Focus on coordination rather than business logic
* Use event-driven architecture for loose coupling
* Handle dependencies and initialization order properly
* Implement comprehensive error handling
* Create thorough tests for coordination logic
* Document manager responsibilities clearly

For additional information, see:

* :doc:`service_development_guide` - Creating services that managers coordinate
* :doc:`plugin_development_guide` - Plugin integration with managers
* :doc:`panel_development_guide` - Panel integration with managers
* :doc:`/core/index` - Core manager API references
