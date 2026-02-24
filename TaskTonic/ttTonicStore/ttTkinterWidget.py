import tkinter as tk
from .. import ttSparkleStack
from ..ttTonic import ttTonic


class ttTkinterMixin:
    """
    Voegt de 'tttk' functionaliteit toe aan Tkinter widgets.
    """

    def _get_custom_prefixes(self):
        return {'tttk': self._bind_tk_event}

    def _bind_tk_event(self, prefix, sparkle_name):
        # Format: tttk__widget_name__event_or_command
        base_name = sparkle_name[6:]  # Haal 'tttk__' eraf

        if "__" not in base_name:
            raise RuntimeError(f"Invalid naming for sparkle '{sparkle_name}'. Expected tttk__widget__event.")

        w_name, e_name = base_name.rsplit("__", 1)

        if not hasattr(self, w_name):
            raise RuntimeError(f"Widget '{w_name}' not found during binding of '{sparkle_name}'.")

        widget = getattr(self, w_name)
        tonic_wrapper = getattr(self, sparkle_name)

        # Bepaal of het een attribuut 'command' is of een reguliere event binding
        if e_name == "command":
            widget.configure(command=tonic_wrapper)
        else:
            # Bijv. e_name == "<Button-1>" of "<Return>"
            widget.bind(e_name, tonic_wrapper)


class ttTkinterFrame(ttTkinterMixin, tk.Frame, ttTonic):
    def __init__(self, parent=None, **kwargs):
        if getattr(self, '_ui_init_done', False):
            return

        ttTonic.__init__(self, **kwargs)

        tk_parent = parent
        tt_context = ttSparkleStack().get_tonic()

        # Vind de juiste master/parent
        if tk_parent is None and isinstance(tt_context, (tk.Tk, tk.Frame)):
            tk_parent = tt_context
        elif tk_parent is None and hasattr(self.base, 'root'):
            tk_parent = self.base.root

        tk.Frame.__init__(self, tk_parent)
        self.setup_ui()
        self._ui_init_done = True

    def setup_ui(self):
        """Override deze functie om je widgets aan te maken"""
        pass
