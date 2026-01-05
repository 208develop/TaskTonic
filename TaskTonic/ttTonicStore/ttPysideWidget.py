import re
from PySide6.QtWidgets import QWidget, QMainWindow
from PySide6.QtCore import QObject, Qt

from ..ttEssence import __ttEssenceMeta
from ..ttTonic import ttTonic

# Dynamische resolutie van de Qt Metaclass
PySideMeta = type(QObject)


class ttPysideMeta(__ttEssenceMeta, PySideMeta):
    """
    Lost het metaclass conflict op tussen TaskTonic (ttEssence) en PySide6 (QObject).
    """
    pass

class ttPysideMixin:
    """
    Voegt de 'ttqt' functionaliteit toe aan widgets.
    """

    def _get_custom_prefixes(self):
        """
        Hook voor ttTonic. Retourneert onze prefix en de binder methode.
        """
        # We gebruiken de SmartPrefix om compatibel te zijn met de logica in ttTonic
        return {'ttqt': self._bind_qt_event}

    def _bind_qt_event(self, prefix, sparkle_name):
        """
        Deze methode wordt door ttTonic aangeroepen voor elke gevonden 'ttqt' method.
        sparkle_name is de naam van de 'interface method' (bijv. ttqt__btn__clicked)
        die ttTonic al heeft omgezet naar een queue-wrapper.
        """
        # 1. Parse de naam: ttqt__(widget)__(signaal)
        # We halen 'ttqt__' eraf.
        base_name = sparkle_name[6:]  # len('ttqt__') == 6

        # We zoeken de LAATSTE dubbele underscore om widget en signaal te scheiden.
        # Dit staat toe dat widget namen zelf dubbele underscores bevatten (bv. self.main__btn).
        if "__" not in base_name:
            raise RuntimeError(f"Invalid naming for sparkle '{sparkle_name}'. Expected ttqt__widget__signal.")

        w_name, s_name = base_name.rsplit("__", 1)

        # 2. Vind het widget
        if not hasattr(self, w_name):
            # Dit kan gebeuren als de UI nog niet is opgebouwd bij init.
            # Zorg dat setup_ui() wordt aangeroepen vòòr super().__init__().
            raise RuntimeError(f"Widget '{w_name}' not found during binding of '{sparkle_name}'.")

        widget = getattr(self, w_name)

        # 3. Vind het signaal
        if not hasattr(widget, s_name):
            raise RuntimeError(f"Error: Signal '{s_name}' not found on '{w_name}'.")

        signal = getattr(widget, s_name)

        # 4. Haal de wrapper op die ttTonic heeft gemaakt
        # Deze wrapper zet de taak op de queue.
        tonic_wrapper = getattr(self, sparkle_name)

        # 5. Verbinden!
        try:
            signal.connect(tonic_wrapper)
            # print(f"[ttPyside] Bound {w_name}.{s_name} -> {sparkle_name}")
        except Exception as e:
            raise RuntimeError(f"[ttPyside] Failed to connect {sparkle_name}: {e}")


class ttPysideWidget(ttPysideMixin, QWidget, ttTonic, metaclass=ttPysideMeta):
    def __init__(self, parent=None, **kwargs):
        qt_parent = parent
        tt_context = kwargs.get('context')
        if qt_parent is None and isinstance(tt_context, QObject):
            qt_parent = tt_context

        QWidget.__init__(self, qt_parent)
        ttTonic.__init__(self, **kwargs)
        self.setup_ui()

    def setup_ui(self):
        pass

    def closeEvent(self, event):
        if self.finishing:
            event.accept()
        else:
            event.ignore()
            self.finish()

    def ttse__on_finished(self):
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.close()


class ttPysideWindow(ttPysideMixin, QMainWindow, ttTonic, metaclass=ttPysideMeta):
    def __init__(self, parent=None, **kwargs):
        qt_parent = parent
        tt_context = kwargs.get('context')
        if qt_parent is None and isinstance(tt_context, QObject):
            qt_parent = tt_context

        QMainWindow.__init__(self, qt_parent)
        ttTonic.__init__(self, **kwargs)

    def closeEvent(self, event):
        if self.finishing:
            event.accept()
        else:
            event.ignore()
            self.finish()

    def ttse__on_finished(self):
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.close()