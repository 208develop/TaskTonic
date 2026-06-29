# TaskTonic Services & Singleton Architecture

<img src="../assets/tasktonic-service.png" align="left" width="350" style="margin-right: 25px; margin-bottom: 20px; border-radius: 8px;" alt="TaskTonic Philosophy">

When building complex, asynchronous applications, the need often arises for central components that must be shared across multiple subtasks (Tonics) without corrupting each other's data streams or internal states. In traditional concurrency models, this inevitably leads to global variables or complex, manually written Singleton patterns riddled with error-prone thread-locks.

TaskTonic solves this fundamentally through the runtime architecture of the `ttLiquid` metaclass (`__ttLiquidMeta`), which seamlessly integrates the Singleton pattern at the framework level.

---

## 1. What is a Service?

A Service in TaskTonic is a specialized `ttTonic` class that is managed as a strict Singleton. The framework's metaclass guarantees that exactly one instance of the Service exists throughout the entire lifecycle of the application (within the scope of the active `ttLedger`).

When any Tonic attempts to instantiate a Service, the following mechanism is triggered:

1. **First Call (Creation):** The metaclass intercepts the call, constructs the unique instance via `super().__call__()`, executes `__init__()` and `_tt_post_init_action()` exactly once, and registers the Service in the central `ttLedger` under its unique service name.
2. **Subsequent Calls (Access):** The framework intercepts the creation attempt, identifies the already registered instance in the ledger, and immediately returns this existing reference. The `__init__()` constructor is **not** executed again.

---

## 2. Architectural Use Cases

You should use the Service pattern exclusively for central resources that must be unique and shared across the entire application:

- **Database Managers:** A central connection pool (`DatabaseService`).
- **Hardware Interfaces:** A single-point-of-entry for serial ports or USB controllers to prevent data corruption from concurrent writes.
- **Shared State Spaces:** Central storage facilities like a `DigitalTwin` (built on top of `ttStore`).
- **Network/API Sockets:** Shared HTTP/REST clients or TCP/IP handlers that need to centrally manage authentication tokens and rate-limiting.

---

## 3. Implementing a Service

Building a Service requires a strict separation between one-time configuration parameters (prefixed with `srv_`) and per-access parameters (prefixed with `ctxt_`).

### Step 1: Class-level Identification

A Service defines itself by setting the class attribute `_tt_is_service` to a unique string identifier. This is the key the `ttLedger` uses to register and look up the Singleton.

### Step 2: `__init__` (One-time Setup)

The constructor is executed exclusively during the very first instantiation of the Service.

- Capture parameters here that are crucial for the initial setup (e.g., `srv_db_url`).
- **Strict Framework Rule:** You *must* always accept `**kwargs` and pass them through to `super().__init__(**kwargs)` to avoid breaking internal bootstrapping and context routing.

### Step 3: `_tt_init_service_base` (Per-Access Hook)

Unlike the constructor, `_tt_init_service_base` is executed by the metaclass **upon every access** to the Service (including the very first creation). This is the hook where the Service discovers *who* is currently calling it.

- The first positional parameter the framework provides is `base` (the Tonic invoking the Service).
- Capture dynamic parameters here (e.g., `ctxt_access_level`).

### 🚨 Crucial for Thread-Safety: Registration via the Queue

When a Tonic calls the Service, `_tt_init_service_base` is executed *within the thread of the calling component*. If the Service runs on its own Catalyst (and thus its own OS thread), mutating Service attributes directly inside this method is a direct violation of TaskTonic's thread-safety guarantees!

**The Golden Rule:** Use `_tt_init_service_base` exclusively to place an asynchronous Command Sparkle (`ttsc__`) onto the Service's own queue. Let the Service handle the administration in its own thread scope.

## 4. Consuming a Service

A consumer Tonic interacts with a Service by simply instantiating the class. The framework handles the de-duplication behind the scenes.

Python

```
from TaskTonic import ttTonic


class DataAnalyzer(ttTonic):
    def ttse__on_start(self):
        # Request the database. Provide srv_ args in case we are the first.
        # Provide ctxt_ args specific to our own session.
        self.database = SharedDatabaseService(
            srv_db_url="postgresql://localhost:5432/prod",
            ctxt_access_level="write"
        )

    def ttsc__process_measurement(self, measurement_data):
        # Communicate via the service's asynchronous command queue
        self.database.ttsc__write_record(measurement_data)
```

## 5. Advanced Pattern: Decoupling via Service Base Classes

In a clean software architecture, you often want to decouple components from specific implementation details. For example: a Tonic needs a `ConnectionService`, but it shouldn't matter to that Tonic whether this runs via an `IpConnectionService` or a `BluetoothConnectionService`.

TaskTonic supports this by allowing you to define an abstract base class as the Service interface, while you start the concrete implementation under the exact same service name in the `ttFormula`.

### 1. Define the Interface (The Base Class)

Python

```
from TaskTonic import ttCatalyst


class ConnectionService(ttCatalyst):
    """    The universal contract class. Consumers will instantiate this class.    """
    _tt_is_service = "central_connection_service"

    def ttsc__send_packet(self, payload):
        pass
```

### 2. Build the Concrete Implementation

Python

```
class IpConnectionService(ConnectionService):
    """    The actual network implementation.    """
    def __init__(self, srv_host, srv_port, **kwargs):
        super().__init__(**kwargs)
        self.host = srv_host
        self.port = srv_port
        self.to_state("disconnected")

    def ttsc_disconnected__send_packet(self, payload):
        self.log("Error: Cannot send data, socket is closed!")

    def ttsc_connected__send_packet(self, payload):
        # Low-level IP write logic here...
        self.log(f"Data sent to {self.host}: {payload}")
```

### 3. The Binding in the Formula and Consumer

The consumer remains completely decoupled and only requests the base interface. The `ttFormula` determines at startup which concrete variant is loaded into the ledger.

Python

```
class ProductionTonic(ttTonic):
    def ttse__on_start(self):
        # Request the SERVICE via the abstract base class
        self.network = ConnectionService()
        self.network.ttsc__send_packet("Test message")


class MyApplication(ttFormula):
    def creating_starting_tonics(self):
        # 1. Start the CONCRETE service first.
        # This registers itself under 'central_connection_service'
        IpConnectionService(srv_host="10.0.0.15", srv_port=8080)

        # 2. Start the consumers.
        ProductionTonic()
```

## 6. Lifecycle, Dependency Tracing, and Teardown

Services feature a unique, automated cleanup mechanism tied to their active users. However, complex applications often involve Services that use *other* Services (e.g., an IP Logger that uses a Socket Handler, which in turn uses a Selector Service).

### The Circular Dependency Problem

If services blindly wait for their `service_bases` (clients) to drop to zero before shutting down, System Services can easily form circular deadlocks. For instance, Service A uses Service B, and Service B uses Service A. Neither will ever reach zero clients, creating "zombies" in the Ledger that prevent the application from shutting down cleanly.

### The Solution: Service Dependency Tracing

To solve this, TaskTonic implements **Service Dependency Tracing** via the `_tt_depending_services` mechanism.

When a Service creates a child Tonic or requests another Service, the framework invisibly tags that child with the name of the parent Service. This creates an execution context "stamboom" (family tree).

### Graceful Top-Down Teardown Flow

Because of this tagging, the framework knows exactly the difference between a "real application client" (like a UI widget or MainApp) and an "internal worker" (like a nested socket).

When a consumer Tonic ends its lifecycle and calls `finish()`, a top-down cascade effect triggers:

1. **Notification:** The finishing consumer notifies the Services it used that it is disconnecting.
  
2. **De-registration:** The Service intercepts this and removes the consumer from its unique `service_bases` Set.
  
3. **Smart Teardown Check:** The Service runs the internal system sparkle `_ttss__on_service_base_removed()`. Instead of simply counting the list length, it iterates over the remaining clients and checks their tags.
  
4. **The Decision:** It asks: *"Are the remaining clients real applications, or are they just internal workers marked with my own service name?"*
  
5. **The Closure:** If no *real* clients are left, the Service concludes its job is done. It automatically triggers `self.finish()`, stopping its state machine, deregistering from the Ledger, and firing a `ttsc__finish()` command down to all its internal children/infusions to clean up OS resources.
  

*(Note: If you need to perform custom administration cleanup when a client disconnects, you can still override the optional user-level hook `ttse__on_service_base_removed(self, removed_base_id, bases_left)` in your Service class).*