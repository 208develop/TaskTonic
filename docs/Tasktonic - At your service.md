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
* **Database Managers:** A central connection pool (`DatabaseService`).
* **Hardware Interfaces:** A single-point-of-entry for serial ports or USB controllers to prevent data corruption from concurrent writes.
* **Shared State Spaces:** Central storage facilities like a `DigitalTwin` (built on top of `ttStore`).
* **Network/API Sockets:** Shared HTTP/REST clients or TCP/IP handlers that need to centrally manage authentication tokens and rate-limiting.

---

## 3. Implementing a Service

Building a Service requires a strict separation between one-time configuration parameters (prefixed with `srv_`) and per-access parameters (prefixed with `ctxt_`).

### Step 1: Class-level Identification
A Service defines itself by setting the class attribute `_tt_is_service` to a unique string identifier. This is the key the `ttLedger` uses to register and look up the Singleton.

### Step 2: `__init__` (One-time Setup)
The constructor is executed exclusively during the very first instantiation of the Service.
* Capture parameters here that are crucial for the initial setup (e.g., `srv_db_url`).
* **Strict Framework Rule:** You *must* always accept `**kwargs` and pass them through to `super().__init__(**kwargs)` to avoid breaking internal bootstrapping and context routing.

### Step 3: `_tt_init_service_base` (Per-Access Hook)
Unlike the constructor, `_tt_init_service_base` is executed by the metaclass **upon every access** to the Service (including the very first creation). This is the hook where the Service discovers *who* is currently calling it.
* De eerste positionele parameter die het framework meegeeft is `base` (de Tonic die de Service aanroept).
* Capture dynamic parameters here (e.g., `ctxt_access_level`).

### 🚨 Crucial for Thread-Safety: Registration via the Queue
When a Tonic calls the Service, `_tt_init_service_base` is executed *within the thread of the calling component*. If the Service runs on its own Catalyst (and thus its own OS thread), mutating Service attributes directly inside this method is a direct violation of TaskTonic's thread-safety guarantees!

**The Golden Rule:** Use `_tt_init_service_base` exclusively to place an asynchronous Command Sparkle (`ttsc__`) onto the Service's own queue. Let the Service handle the administration in its own thread scope.

```python
from TaskTonic import ttTonic


class SharedDatabaseService(ttTonic):
    # The unique framework key for the Ledger
    _tt_is_service = "SharedDatabaseService"

    def __init__(self, srv_db_url, **kwargs):
        """
        Executed EXACTLY once during the very first call.
        """
        super().__init__(**kwargs)
        self.db_url = srv_db_url
        self.authorized_clients = {}
        self.log(f"Database connected at: {self.db_url}")

    def _tt_init_service_base(self, base, ctxt_access_level="read", **kwargs):
        """
        Executed ON EVERY CALL to the service.
        WARNING: This runs in the thread of the CALLER (base)!
        Forward the data directly to the safe Catalyst queue via a sparkle.
        """
        if base is None:
            return

        # Place the registration safely on this service's own queue
        self.ttsc__register_client(base, ctxt_access_level)

    def ttsc__register_client(self, client_instance, access_level):
        """
        Runs SAFELY within the Service Catalyst's own thread.
        """
        client_id = client_instance.id
        self.authorized_clients[client_id] = {
            "instance": client_instance,
            "level": access_level
        }
        self.log(f"Client {client_id} registered with level: {access_level}")
```

---

## 4. Consuming a Service

A consumer Tonic interacts with a Service by simply instantiating the class. The framework handles the de-duplication behind the scenes.

```python
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

---

## 5. Advanced Pattern: Decoupling via Service Base Classes

In a clean software architecture, you often want to decouple components from specific implementation details. For example: a Tonic needs a `ConnectionService`, but it shouldn't matter to that Tonic whether this runs via an `IpConnectionService` or a `BluetoothConnectionService`.

TaskTonic supports this by allowing you to define an abstract base class as the Service interface, while you start the concrete implementation under the exact same service name in the `ttFormula`.

### 1. Define the Interface (The Base Class)
```python
from TaskTonic import ttCatalyst


class ConnectionService(ttCatalyst):
    """
    The universal contract class. Consumers will instantiate this class.
    """
    _tt_is_service = "central_connection_service"

    def ttsc__send_packet(self, payload):
        pass
```

### 2. Build the Concrete Implementation
```python
class IpConnectionService(ConnectionService):
    """
    The actual network implementation.
    """
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

```python
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

---

## 6. Lifecycle and Teardown Mechanism

Services feature a unique, automated cleanup mechanism tied to their active users.

### Automatic Infusion Tracking
When an existing Service is requested again anywhere in the application, the metaclass intercepts this and performs the following administrative steps:
1. The calling Tonic (`base`) is automatically appended to the Service's internal `service_bases` list (`tonic.service_bases.append(base)`).
2. The Service is registered as an active dependency on the caller via `base._tt_add_infusion(tonic)`.

> **Architecture Note (First Creation Isolation):**
> By design, when a Service is created for the *very first time* by a Tonic, the framework explicitly sets its `base` to `None`. This isolates the new Service from the caller's lifecycle, preventing the Service from being destroyed if the instantiating worker finishes early. On all *subsequent* calls, the caller is properly registered as an active dependency.

### Graceful Teardown Flow
Because the Service accurately tracks which Tonics depend on it, it knows exactly when it is no longer needed. When a consumer Tonic ends its lifecycle and calls `finish()`, a cascade effect triggers within `ttTonic.py`:

1. The finishing consumer Tonic executes its `_ttss__on_finished` routine.
2. It iterates through its active `infusions` and calls `ttsc__finish()` on the Service.
3. The Service intercepts this in its own `ttsc__finish()` method and recognizes that the caller is part of its `service_bases`.
4. The Service removes this specific client from its list: `self.service_bases.remove(calling_tonic)`.
5. **The Closure:** The Service checks its remaining dependencies. If there are *no* active components left (`len(self.service_bases) <= 0`), the Service concludes its job is done. It triggers its own teardown sequence, calling `ttse__on_service_base_completed` to notify listeners, stops its state machine, and permanently removes itself from the `ttLedger`.
