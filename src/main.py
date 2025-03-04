import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer
from src.ui.main_window import MainWindow


def main():
    # Initialize the application
    app = QApplication(sys.argv)
    app.setApplicationName("PCPulse")
    app.setApplicationDisplayName("PCPulse Hardware Monitor")

    # Create main window
    window = MainWindow()
    window.show()

    # Use a timer to keep event loop responsive
    timer = QTimer()
    timer.timeout.connect(lambda: None)
    timer.start(100)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
