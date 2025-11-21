# The Service (Singleton) Pattern

This document explains how to create and use "Services" within the TaskTonic framework. A Service is a special type of
`ttTonic` class that is managed as a **Singleton**, ensuring only one instance ever exists.

It also introduces the concept of a "per-access" hook (`_init_service`) for context-aware interactions.

---

## 1. What is a Service?

A Service is a `ttTonic` class that is guaranteed to have **only one instance** throughout the application's lifecycle.

The `ttMeta` metaclass (which `ttEssence` and `ttTonic` use) manages this. When you try to create an instance of a
Service:

* **The First Time:** The metaclass creates the instance, runs its `__init__` and `_init_post_action` methods once, and
  stores it in the `ttLedger` under a unique name.
* **Every Subsequent Time:** The metaclass intercepts the call, finds the *existing* instance in the `ttLedger`, and
  returns it immediately. `__init__` is **not** called again.

### Key Feature: The `_init_service` Hook

A Service is "context-aware." Every time a Service is accessed (both on creation *and* on subsequent retrievals), the
metaclass will call its `_init_service` method.

This allows you to pass context-specific parameters (e.g., `ctxt_ip`, `ctxt_access_level`) that are processed *every
time*, while one-time setup parameters (e.g., `srv_api_key`) are only processed *once* in `__init__`.

---

## 2. Application Examples

You should use this pattern for any class that needs to be unique and shared across your entire application. 📈

* **Logging:** A `LoggerService` that all other `ttTonic` tasks call to write logs. You only want one instance managing
  the log file or screen output.
* **Configuration:** A `ConfigService` that loads a `.ini` or `.yaml` file once and provides settings to any task that
  asks for it.
* **Database Management:** A `DatabaseService` that manages a single connection pool for the entire application.
* **API Clients:** An `ApiService` that handles a single OAuth2 token, rate limiting, and authentication for a shared
  REST API.
* **Hardware Control:** A `SerialService` that manages a single connection to a piece of hardware, preventing multiple
  tasks from trying to access the same port.

---

## 3. How to Create a Service

Creating a service is simple and follows four steps.

### Step 1: Inherit from `ttTonic`

Your service class must inherit from `ttTonic` (or any class that inherits from `ttEssence`).

```python
class MyService(ttTonic):
    pass
```

### Step 2: Set the Service Flag

Set the `_tt_is_service` class variable to a unique string name. This name is how the `ttLedger` will identify your
singleton.

```python
class MyService(ttTonic):
    # This tells the metaclass to treat this class as a
    # service identified by the name "MyUniqueService"
    _tt_is_service = "MyUniqueService"
```

### Step 3: Implement `__init__` (One-Time Setup)

This is your standard constructor. It is **only called once** when the service is first created.

* Use parameters prefixed with `srv_` (service) for one-time setup (e.g., `srv_api_key`).
* **Crucially:** You must also accept any context parameters (e.g., `ctxt_...`) and `**kwargs` so you can cleanly pass
  the correct arguments to `super().__init__`.

```python
class MyService(ttTonic):
    _tt_is_service = "MyUniqueService"

    def __init__(self, srv_api_key, ctxt_ip=None, **kwargs):
        """
        Runs ONCE.
        Catches the 'srv_api_key' for setup.
        Catches 'ctxt_ip' (and others) just to remove them
        before calling super().
        """
        print(f"  MyService __init__: Service is being CREATED.")
        print(f"  > Setting API Key to: {srv_api_key}")
        
        # 'name' is in kwargs, passed by the metaclass
        super().__init__(**kwargs) 
        
        self.api_key = srv_api_key
        self.context_data = {}
```

### Step 4: Implement `_init_service` (Per-Access Hook)

This method is **called every time** the service is accessed, including the first time (right after
`_init_post_action`).

* Use parameters prefixed with `ctxt_` (context) for per-access logic.
* Use `**kwargs` to safely ignore the one-time `srv_` parameters that are also passed in.

```python
class MyService(ttTonic):
    _tt_is_service = "MyUniqueService"

    def __init__(self, srv_api_key, ctxt_ip=None, **kwargs):
        # ... (from Step 3) ...
        print(f"  MyService __init__: Service is being CREATED.")
        print(f"  > Setting API Key to: {srv_api_key}")
        super().__init__(**kwargs) 
        self.api_key = srv_api_key
        self.context_data = {}

    def _init_service(self, context, ctxt_ip, **kwargs):
        """
        Runs EVERY time.
        Catches 'context' and 'ctxt_ip'.
        Ignores 'srv_api_key' (which is in **kwargs).
        """
        if context is None:
            return
            
        print(f"  MyService _init_service__: Context '{context.name}' "
              f"is accessing from IP '{ctxt_ip}'")
        
        # Store context-specific data
        self.context_data[context.id] = {'ip': ctxt_ip}

    def get_ip_for(self, context):
        return self.context_data.get(context.id, {}).get('ip')
```

### **A Critical Warning on Context and Lifecycle**

> **BE AWARE:** When creating a service, be careful with its `context`. If you create a service *within the context of
another essence* (e.g., `MyService(context=another_task)`), it becomes a child of that essence via the `bind` mechanism.
>
> If `another_task` is finished, it will call `finish()` on all its children. This **will finish and unregister your
service singleton for everyone**.
>
> **Recommendation:** It is almost always better to create services with `context=None` (making them top-level) or from
a single, persistent root task (e.g., your "formula" or main application runner).

---

# 5. Using a Service Base Class

Sometimes you want to use a service, without knowing what kind of service implementation is used. For instance when
you use an `ConnectionService`, that can be een `IpConnectionService` or `BluToothConnectionService`.

## 5.1 How to
For that create a service base class (or interface) that provides a universal contract for a specific type of 
functionality (e.g., "connecting" or "logging"). This approach is central to creating a decoupled and 
maintainable architecture.

In the formula the implementation of a specific service is started. The service name wil be the same for every
implementation. Tonics that are using the service should depend on the universal base class and use the service name.
The specific service, with that name, will be used due to the singleton service implementation. 


## 5.2 Example: ConnectionService

Let's walk through an example with a universal `ConnectionService` (the base class) and two specific implementations:
`IpConnectionService` and `BluToothConnectionService`.

### 1. Defining the Services

First, we define the abstract base class and the concrete implementations. The Tonics will only know about
`ConnectionService`.

```python
# === services/connection_service.py ===
from TaskTonic import *


class ConnectionService(ttCatalyst):
  """
  The universal base class (interface) for all connection services.
  Tonics will depend on this class.
  
  It defines the 'contract' that all connection services must follow.
  """
  _tt_is_service = 'connection_service'

  def ttsc__connect(self):
    pass

  def ttsc__disconnect(self):
    pass

  def ttsc__transmit(self, data):
    pass


# === services/ip_connection.py ===
from .connection_service import ConnectionService


class IpConnectionService(ConnectionService):
  """
  Specific implementation for IP-based connections (e.g., WiFi, Ethernet).
  """

  def __init__(self, context=None, host: str, port: int):
    super().__init__(context=context, log_mode='quiet')
    self.host = host
    self.port = port
    self.status = "Disconnected"
    self.log(f"IpConnectionService: Initialized for {host}:{port}")
    self.to_state('disconnected')

  def ttsc__disconnected__connect(self):
    # Specific logic for IP connection
    self.log(f"Connecting via IP to {self.host}:{self.port}...")
    # ... implementation details ...
    self.status = f"Connected (IP to {self.host})"
    self.log("IpConnectionService: Established.")
    self.to_state('connected')

  def ttsc__connected__disconnect(self):
    self.log("Disconnecting IP connection.")
    self.to_state('disconnected')

  def ttsc__connected__transmit(self, data):
    self.log(f'Tranmitting: {data}')
    # ... implementation details ...

  def ttse__connected__on_exit(self):
# implement disconnection


# === same for all other connection services

# === myTonic 
class MyTonic(ttTonic):
  def ttse__on_start(self):
    from services.connection_service import ConnectionService
    self.conn = self.bind(ConnectionService) # use the service base class
    self.conn.ttsc__connect()


#  == Formula
class MyFormula(ttFormula):
  def creating_starting_tonics(self):
    IpConnectionService(context=-1, 'localhost', 123456) # startup the ip connection service
    MyTonic(context=-1)

```

## 6. Full Example

Here is a complete example showing how two different tasks (`RootTask` and `WorkerTask`) access the same service.

```python
from TaskTonic import *

class RootTask(ttTonic):
    """A standard, non-service task."""
    pass
    
class WorkerTask(ttTonic):
    """Another standard, non-service task."""
    pass

class NetService(ttTonic):
    """
    A singleton service that manages a network resource.
    """
    
    # 1. Set the unique service name
    _tt_is_service = "NetworkManager"
    
    def __init__(self, srv_host_url, ctxt_port=None, **kwargs):
        """
        Runs ONCE to configure the service.
        """
        self.log(f"  NetService __init__: CONNECTING to {srv_host_url}...")
        
        # Pass standard args (name, context) up to ttEssence
        super().__init__(**kwargs) 
        
        self.host_url = srv_host_url
        self.context_ports = {}

    def _init_service(self, context, ctxt_port, **kwargs):
        """
        Runs EVERY time to register context-specific info.
        """
        self.ttsc__new_service_entry(context, ctxt_port)
                
    def ttsc__new_service_entry(context, ctxt_port):
        self.log(f"  NetService _init_service__: Context '{context.name}' "
                 f"registered on port {ctxt_port}.")
        self.context_ports[context.id] = ctxt_port
        
# --- Example Usage ---
if __name__ == "__main__":

    print("--- 1. Creating Tasks ---")
    root = RootTask(name="Root")
    worker = WorkerTask(name="Worker", context=root)

    print("\n--- 2. RootTask requests the NetService ---")
    # This is the FIRST call. __init__ will run.
    # We create it with context=None as recommended.
    service1 = NetService(
        context=None,
        srv_host_url="httpsa://api.tasktonic.com",
        ctxt_port=8080
    )
    # Manually log access for root
    service1._init_service(context=root, ctxt_port=8080)


    print("\n--- 3. WorkerTask requests the SAME NetService ---")
    # This is the SECOND call. __init__ is SKIPPED.
    service2 = NetService(
        context=worker,
        srv_host_url="[https://api.IGNORED.com](https://api.IGNORED.com)", # This is ignored
        ctxt_port=9090
    )
    
    print("\n--- 4. Verification ---")
    print(f"service1 is service2: {service1 is service2}")
    print(f"Service Host URL: {service1.host_url}")
    print(f"Root's Port: {service1.context_ports[root.id]}")
    print(f"Worker's Port: {service1.context_ports[worker.id]}")
