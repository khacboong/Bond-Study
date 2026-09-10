from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication, QStyleFactory

from .navigation import Main
from .theme import APP_STYLE


def main():
    """Start Bond Study and return the Qt event-loop exit code."""
    app = QApplication(sys.argv)
    app.setStyle(QStyleFactory.create("Fusion"))
    app.setStyleSheet(APP_STYLE)
    window = Main()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
