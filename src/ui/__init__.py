"""
PCPulse UI components package
"""

from src.ui.main_window import MainWindow
from src.ui.dashboard import DashboardWidget
from src.ui.sensor_widget import TemperatureSensorWidget
from src.ui.themes import apply_dark_theme

__all__ = ['MainWindow', 'DashboardWidget', 'TemperatureSensorWidget', 'apply_dark_theme']
