# TaskTonic & PySide6 Integration Guide

Building graphical user interfaces in Python often leads to a common trap: a background calculation or a long-running process freezes the entire application window. Traditionally, developers solve this by wrestling with `QThread`, custom signals, and complex worker classes. 

TaskTonic eliminates this boilerplate entirely. By integrating PySide6 directly into the TaskTonic execution model, your UI components become state-aware, asynchronous agents (Tonics) that never freeze, all without manually spawning a single thread.

## The API Explained: How the Integration Works

To make PySide6 and TaskTonic work together seamlessly, the framework provides three main components: a specialized Catalyst, specialized UI Tonics, and a powerful naming convention for event binding.

### 1. The Qt Engine: `ttPyside6Ui`
In a standard TaskTonic application, the `tt_main_catalyst` runs a continuous `while` loop to process the Sparkle queue. However, a GUI framework like PySide6 requires its own blocking loop (`QApplication.exec()`) to draw the screen and capture mouse clicks. 

The `ttPyside6Ui` class solves this clash. You set this class as your `tt_main_catalyst` inside your `ttFormula`. Under the hood, it creates a specialized queue. Whenever a new Sparkle is placed on the queue, it generates a custom thread-safe `QEvent` and posts it to the Qt event loop. This ensures that every Sparkle affecting the UI is safely executed on the main Qt thread, preserving complete thread safety without freezing the visual interface.

### 2. The UI Tonics: `ttPysideWindow` & `ttPysideWidget`
Instead of inheriting from the standard `ttTonic`, your UI components should inherit from `ttPysideWindow` (for main application windows) or `ttPysideWidget` (for internal panes and components). 

These classes handle the complex metaclass resolution required to blend Python's `QObject` with TaskTonic's `ttLiquid`. They also automatically capture the Qt close events (`closeEvent`) and redirect them to the TaskTonic lifecycle (`self.finish()`), ensuring your application shuts down gracefully without leaving zombie threads behind.

### 3. The Magic Prefix: `ttqt__`
TaskTonic uses introspection to build your application logic. For PySide6, it introduces the `ttqt__` prefix. 

When your UI Tonic initializes, the framework scans your methods. If it finds a method following the pattern `ttqt_[state]__[widget_name]__[signal_name]`, it automatically connects the Qt signal to the Catalyst queue.

For example, if you have a `QPushButton` stored as `self.btn_submit`, and you define a method named `ttqt__btn_submit__clicked(self)`, TaskTonic automatically executes `self.btn_submit.clicked.connect(your_method_wrapper)`. You never have to write `.connect()` manually again. The execution is automatically delegated to the atomic Sparkle queue.

---

## Hello World Example: The State-Driven Toggle Button

This example demonstrates how to build a simple window with a button that toggles a greeting. Notice how the application logic relies entirely on the built-in State Machine, keeping the code clean and free of boolean flags.

```python
from PySide6.QtWidgets import QVBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt
from TaskTonic import ttFormula, ttLog
from TaskTonic.ttTonicStore import ttPyside6Ui, ttPysideWindow, ttPysideWidget


class ToggleGreetingWidget(ttPysideWidget):

    def setup_ui(self):
        self.layout = QVBoxLayout(self)

        # Label component named: lbl_text
        self.lbl_text = QLabel("--")
        self.lbl_text.setAlignment(Qt.AlignCenter)
        self.lbl_text.setStyleSheet("font-size: 20px; padding: 25px; background: #222; color: #fff;")
        self.layout.addWidget(self.lbl_text)

        # Button component named: btn_toggle
        self.btn_toggle = QPushButton("Toggle Greeting")
        self.btn_toggle.setStyleSheet("font-size: 16px; padding: 10px;")
        self.layout.addWidget(self.btn_toggle)

    def ttse__on_start(self):
        self.to_state("world")

    # --- STATE: WORLD ---
    def ttse_world__on_enter(self):
        self.lbl_text.setText("Hello World")

    def ttqt_world__btn_toggle__clicked(self):
        self.to_state("tasktonic")

    # --- STATE: TASKTONIC ---
    def ttse_tasktonic__on_enter(self):
        self.lbl_text.setText("Hello TaskTonic")

    def ttqt_tasktonic__btn_toggle__clicked(self):
        self.to_state("world")


class MainWindow(ttPysideWindow):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setWindowTitle("TaskTonic PySide6 Hello World")
        self.resize(400, 200)

        self.toggle_widget = ToggleGreetingWidget()
        self.setCentralWidget(self.toggle_widget)

    def ttse__on_start(self):
        self.show()


class HelloPySideFormula(ttFormula):

    def creating_formula(self):
        return {
            'tasktonic/log/to': 'screen',
            'tasktonic/log/default': 'full',
        }

    def creating_main_catalyst(self):
        ttPyside6Ui(name='tt_main_catalyst')

    def creating_starting_tonics(self):
        MainWindow()


if __name__ == "__main__":
    HelloPySideFormula()
```

---

## Behind the Scenes: How the Example Executes

When you run the code above, a highly orchestrated sequence of events occurs silently:

1. **Initialization:** The `HelloPySideFormula` configures the application. It instantiates the `ttPyside6Ui` as the main engine, handing control over to the Qt event loop, while silently keeping the TaskTonic queues alive in the background.
2. **State Bootstrapping:** When `ToggleGreetingWidget` starts, `self.to_state("world")` transitions the internal state machine. The framework detects this state change and automatically fires the `ttse_world__on_enter` Sparkle, which updates the label to "Hello World".
3. **Late State Binding:** The magic happens when the user clicks the button. The `clicked` signal fires, but instead of executing logic directly, it places a work order on the Catalyst queue. When the engine pulls this order a millisecond later, it checks the *current* state of the Tonic. 
4. **The Toggle:** Because the state is `world`, the framework routes the click strictly to `ttqt_world__btn_toggle__clicked`. This method changes the state to `tasktonic`. The next time the user clicks the button, the framework sees the new state and dynamically routes the execution to `ttqt_tasktonic__btn_toggle__clicked`, creating a perfect toggle loop without a single `if/else` statement evaluating the button's status.