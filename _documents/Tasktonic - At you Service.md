# Mastering TaskTonic Services (The Singleton Pattern)

When building complex applications, you often need a central resource that multiple Tonics can share without stepping on each other's toes. In traditional programming, you might use global variables or implement complex Singleton patterns with thread locks. 

TaskTonic provides an elegant, built-in solution for this: **Services** [1].

Here is everything you need to know about what Services are, when to use them, how to create them, and the best practices for context-aware initialization.

---

## 1. What is a Service and When Do You Use It?

A Service is a special `ttTonic` class that is managed as a **Singleton** [1, 2]. The TaskTonic metaclass guarantees that **only one instance of a Service ever exists** throughout your application's lifecycle [3, 4].

When a Tonic tries to create an instance of a Service:
*   **The First Time:** The framework creates the instance, executes its `__init__` method, and registers it in the `ttLedger` [3-5].
*   **Every Subsequent Time:** The framework intercepts the creation, finds the existing instance in the ledger, and returns it. `__init__` is *not* called again [4, 5].

**When to use a Service:**
You should use a Service for any central resource that needs to be unique and shared [6, 7]:
*   **Databases:** A single connection pool manager (`DatabaseService`) [6, 7].
*   **Hardware Control:** A single handler for a serial port to prevent multiple Tonics from sending conflicting bytes (`SerialService`) [7, 8].
*   **State Management:** A centralized data store like the `DigitalTwin` (using `ttStore`) [9].
*   **Logging/Configuration:** A central logger or config file loader [6, 7].

---

## 2. How to Create a Service

Creating a Service requires only a few specific steps. 

### Step 1: The Class Flag
You define a Service by inheriting from `ttTonic` (or another essence) and setting the `_tt_is_service` class variable to a unique string [10, 11]. This string is the name the Ledger uses to identify the singleton [10, 11].

```python
from TaskTonic import ttTonic

class DatabaseService(ttTonic):
    _tt_is_service = "SharedDatabaseService" # Unique identifier
```

### Step 2: `__init__` (One-Time Setup)
Implement your `__init__` method for configuration that should only happen **once** (like connecting to the database) [11, 12]. 
*   **Naming Convention:** Prefix parameters intended for one-time setup with `srv_` (e.g., `srv_db_url`) [12, 13].
*   **Kwargs Rule:** You *must* accept `**kwargs` and pass them to `super().__init__(**kwargs)` so the framework can handle context routing [12, 13].

```python
    def __init__(self, srv_db_url, **kwargs):
        super().__init__(**kwargs)
        self.db_url = srv_db_url
        self.log(f"Connecting to database at {self.db_url} (Happens ONCE)")
        self.connected_clients = {}
```

---

## 3. The `_init_service` Hook (Per-Access Setup)

Because `__init__` only runs once, how does the Service know when a *new* Tonic connects to it? 

TaskTonic provides the **`_init_service`** hook. This method is called by the framework **every single time** a Tonic asks for the Service (including the very first time) [5, 14, 15]. 

*   **Naming Convention:** Prefix parameters intended for per-access setup with `ctxt_` (e.g., `ctxt_access_level`) [13, 16].
*   This is where you register the new client (the `context`) with your Service [17].

### 🚨 Best Practice: Use a Sparkle for Registration!
When a worker Tonic requests your Service, the `_init_service` method is executed *in the calling Tonic's thread*. If your Service is running on its own Catalyst (its own thread), modifying Service variables directly inside `_init_service` violates TaskTonic's thread-safety guarantees!

**The Golden Rule:** Use `_init_service` strictly to put a command (`ttsc__`) onto the Service's queue [18, 19]. Let the Service process the registration in its own time, ensuring atomic thread safety.

```python
    def _init_service(self, context, ctxt_access_level="read", **kwargs):
        """
        Runs EVERY time a Tonic binds this service.
        Runs in the CALLER'S thread. Do not modify state directly!
        """
        if context is None:
            return
            
        # Queue a sparkle to handle the registration safely!
        self.ttsc__register_new_client(context, ctxt_access_level)

    def ttsc__register_new_client(self, context, access_level):
        """
        Runs in the SERVICE'S thread. 100% thread-safe.
        """
        self.log(f"Registering client '{context.name}' with level: {access_level}")
        self.connected_clients[context.id] = {
            'instance': context, 
            'level': access_level
        }
```

---

## 4. How to Use a Service

To use a Service, you simply instantiate it as if it were a normal Tonic [20, 21]. The framework handles the Singleton magic behind the scenes.

```python
class DataAnalyzer(ttTonic):
    def ttse__on_start(self):
        # 1. Ask for the service. 
        # Pass 'srv_' args just in case this is the first time it's created.
        # Pass 'ctxt_' args for this specific analyzer.
        self.db = DatabaseService(
            srv_db_url="postgres://user:pass@localhost",
            ctxt_access_level="write"
        )
        
    def ttsc__save_data(self):
        self.db.ttsc__store_record({"data": "123"})
```

### ⚠️ The Context Trap (Warning!)

By default, when you instantiate a Tonic inside another Tonic, the new Tonic becomes a child of the caller (it binds to the caller's context) [22, 23]. 

If you create a Service from a temporary worker Tonic, the Service becomes a child of that worker [22, 23]. **If the worker finishes, it will recursively finish all its children—killing your shared Service for the entire application!** [22, 23]

**How to avoid this:**
It is highly recommended to create Services at the top level of your application (in your `ttFormula` inside `creating_starting_tonics`) [23, 24]. If you *must* create a Service from inside a worker, explicitly break the context chain by passing `context=None` (or `context=-1`):

```python
    def ttse__on_start(self):
        # By passing context=None, the Service is registered at the root level,
        # completely immune to this worker's lifecycle.
        self.db = DatabaseService(
            context=None, 
            srv_db_url="postgres://..."
        )
        # Manually trigger the access hook for this worker
        self.db._init_service(context=self, ctxt_access_level="read")
```

## Summary Checklist for Services
1. Add `_tt_is_service = "name"` to your class [10, 11].
2. Use `__init__` for one-time setup (`srv_` kwargs) [11, 12].
3. Use `_init_service` for per-client setup (`ctxt_` kwargs) [13, 14, 16].
4. **Always** dispatch a `ttsc__` sparkle inside `_init_service` to modify the Service's internal state [18, 19]. 
5. Instantiate Services at the Formula level to prevent accidental teardowns [22-24].
```