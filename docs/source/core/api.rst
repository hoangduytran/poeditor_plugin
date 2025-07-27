API
===

.. automodule:: core.api
   :members:
   :undoc-members:
   :show-inheritance:

Overview
--------

The API module provides a consistent interface for plugins and components to interact with the application's core functionality. It abstracts the underlying implementation details and provides a stable contract for extensions to build upon.

Class Reference
-------------

CoreAPI
~~~~~~

Main API class that provides access to various core services:

.. code-block:: python

    class CoreAPI:
        def __init__(self):
            self._services = {}
            self._event_bus = EventBus()
            
        def register_service(self, service_id, service_instance):
            """Register a service with the API."""
            self._services[service_id] = service_instance
            
        def get_service(self, service_id):
            """Get a service by ID."""
            if service_id not in self._services:
                raise ServiceNotFoundError(f"Service '{service_id}' not found")
            return self._services[service_id]
            
        @property
        def event_bus(self):
            """Get the event bus for pub/sub communication."""
            return self._event_bus

EventBus
~~~~~~~

Event bus implementation for publish/subscribe communication:

.. code-block:: python

    class EventBus:
        def __init__(self):
            self._subscribers = {}
            
        def subscribe(self, event_type, callback):
            """Subscribe to an event."""
            if event_type not in self._subscribers:
                self._subscribers[event_type] = []
            self._subscribers[event_type].append(callback)
            
        def unsubscribe(self, event_type, callback):
            """Unsubscribe from an event."""
            if event_type in self._subscribers and callback in self._subscribers[event_type]:
                self._subscribers[event_type].remove(callback)
                
        def publish(self, event_type, **data):
            """Publish an event with data."""
            if event_type in self._subscribers:
                for callback in self._subscribers[event_type]:
                    callback(**data)

ServiceNotFoundError
~~~~~~~~~~~~~~~~~~

Exception raised when a requested service is not found:

.. code-block:: python

    class ServiceNotFoundError(Exception):
        """Raised when a requested service is not available in the API."""
        pass

Usage Examples
------------

Accessing the API
~~~~~~~~~~~~~~

.. code-block:: python

    # In a plugin or component
    from core.api import CoreAPI
    
    # Get the API instance (typically provided during initialization)
    api = get_api_instance()
    
    # Access a service
    file_service = api.get_service("file_service")
    file_service.open_file("/path/to/file.txt")

Working with Services
~~~~~~~~~~~~~~~~~~

.. code-block:: python

    # Registering a service
    class MyService:
        def __init__(self):
            self.name = "My Service"
            
        def do_something(self):
            print("Doing something...")
    
    my_service = MyService()
    api.register_service("my_service", my_service)
    
    # Using a service
    service = api.get_service("my_service")
    service.do_something()

Using the Event Bus
~~~~~~~~~~~~~~~~

.. code-block:: python

    # Subscribe to an event
    def on_file_opened(file_path, encoding):
        print(f"File opened: {file_path} with encoding {encoding}")
    
    api.event_bus.subscribe("file.opened", on_file_opened)
    
    # Publish an event
    api.event_bus.publish(
        "file.opened", 
        file_path="/path/to/file.txt", 
        encoding="utf-8"
    )
    
    # Unsubscribe when done
    api.event_bus.unsubscribe("file.opened", on_file_opened)

Service Registration Pattern
-------------------------

Services are typically registered during application startup:

.. code-block:: python

    # Application startup
    api = CoreAPI()
    
    # Register core services
    api.register_service("file_service", FileService())
    api.register_service("editor_service", EditorService())
    api.register_service("translation_service", TranslationService())
    
    # Provide API to plugins
    plugin_manager = PluginManager(api)
    plugin_manager.load_plugins()

Error Handling
-----------

Properly handle service errors:

.. code-block:: python

    from core.api import ServiceNotFoundError
    
    try:
        service = api.get_service("some_service")
        service.do_something()
    except ServiceNotFoundError:
        # Handle missing service
        print("Required service is not available")
    except Exception as e:
        # Handle other errors
        print(f"Error using service: {str(e)}")
