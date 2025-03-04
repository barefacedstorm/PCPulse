from PySide6.QtWidgets import QMainWindow, QTabWidget, QVBoxLayout, QWidget
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QAction

from src.ui.dashboard import DashboardWidget
from src.hardware_monitor import HardwareMonitor
from src.ui.themes import apply_dark_theme

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("PCPulse Hardware Monitor")
        self.resize(1000, 700)

        # Apply dark theme
        apply_dark_theme(self)

        # Create hardware monitor
        self.hardware_monitor = HardwareMonitor(update_interval=1000)

        # Create central widget with tabs
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # Create dashboard
        self.dashboard = DashboardWidget(self.hardware_monitor)
        self.tabs.addTab(self.dashboard, "Dashboard")

        # Create menu
        self.create_menu()

        # Start hardware monitoring
        self.hardware_monitor.start()

    def create_menu(self):
        menu_bar = self.menuBar()

        # File menu
        file_menu = menu_bar.addMenu("&File")

        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # View menu
        view_menu = menu_bar.addMenu("&View")

        refresh_action = QAction("Refresh Now", self)
        refresh_action.triggered.connect(self.hardware_monitor.update_data)
        view_menu.addAction(refresh_action)

    def closeEvent(self, event):
        self.hardware_monitor.stop()
        event.accept()
