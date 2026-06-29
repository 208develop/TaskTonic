# Changelog

## [0.2.0]
🎉 **First Stable Release of TaskTonic (v0.2.0)**

TaskTonic is a Python framework designed to manage application complexity through a unique concurrency model. It allows you to write highly responsive, concurrent applications (like UIs or IoT controllers) without the race conditions and headaches of traditional multi-threading.

### ✨ Key Features in this release:
* **Sparkling Programming:** You figure it out, cheers!!
* **Non-blocking Timers:** Built-in scheduling components (`ttTimerSingleShot`, `ttTimerEveryDay`, etc.) that never freeze your application.
* **Built-in State Machines:** Easy to use, clears up your code.
* **Testing Concurrency:** Yes, really. Look up the `ttDistiller` and find out.
* **UI Integrations:** Optional, ready-to-use wrappers for PySide6 (ready!!) and Tkinter (under construction) (`ttPyside6Ui`, `ttTkinterUi`).
* **Developer Ready:** I hope. It's just out in the open now, please help out. However, it is tested and compatible with `pytest`.

### 🚀 Getting Started
Full documentation and practical use cases can be found in the `_documents` and `examples` directories. 
*(PyPI package installation via `pip install TaskTonic` will be available shortly!)*

## [0.2.1] - 2026-06-01

Refining api after using it in the first project so everything feels like expected 
and redesign of the `Store` for smart central data and state distribution.

### New
- IP logger support, to use with TaskTonic Visual Logger (https://github.com/208develop/tasktonic-visual-logger), for tracking concurrent tasks.

### Changed
- Store and ttStore
   - `ttStore` is a `ttTonic` now, for active store management.
   - Extended subscribing (/room/sensors/*/temp)
   - `StoreLink`, relative path to a `Store` `Item`. You can reach the same `Item` from multiple paths.
   - Some api updates

## [0.2.2] - 2026-06-29
### New
- New networking module with selectorhandler as base. Now supporting tcp / udp / http
- Introduction of https://tasktonic.dev
- AI Context file for learning TaskTonic to AI (on ai.tasktonic.dev)

### Changed
- ttDistiller
  - Support for multiple tonic test (integrations) with new powerful contracts

### Fixed
- When service where depending on each other locking on finish was possible. A dependency tracing mechanism will prevent this. 
- Documentation cleanup
