from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QProgressBar
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor

class TemperatureSensorWidget(QWidget):
    def __init__(self, name, temperature):
        super().__init__()

        # Define temperature thresholds
        self.GOOD_THRESHOLD = 60  # Green below this
        self.WARNING_THRESHOLD = 80  # Yellow between good and warning
        # Red above warning threshold

        # Layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Sensor name
        self.name_label = QLabel(name)
        self.name_label.setMinimumWidth(120)

        # Temperature value
        self.temp_label = QLabel(f"{temperature:.1f}°C")
        self.temp_label.setMinimumWidth(70)

        # Progress bar for visual representation
        self.temp_bar = QProgressBar()
        self.temp_bar.setRange(0, 100)
        self.temp_bar.setValue(min(int(temperature), 100))
        self.temp_bar.setTextVisible(False)

        # Set temperature status color
        self.update_status_color(temperature)

        # Add widgets to layout
        layout.addWidget(self.name_label)
        layout.addWidget(self.temp_label)
        layout.addWidget(self.temp_bar)

    def update_status_color(self, temperature):
        """Update the color of the progress bar based on temperature"""
        style = """
        QProgressBar {
            border: 1px solid #444;
            border-radius: 3px;
            background-color: #333;
            height: 15px;
        }
        """

        if temperature < self.GOOD_THRESHOLD:
            # Good temperature - Green
            style += """
            QProgressBar::chunk {
                background-color: #4CAF50;
                border-radius: 2px;
            }
            """
            self.temp_label.setStyleSheet("color: #4CAF50;")
        elif temperature < self.WARNING_THRESHOLD:
            # Warning temperature - Yellow/Orange
            style += """
            QProgressBar::chunk {
                background-color: #FF9800;
                border-radius: 2px;
            }
            """
            self.temp_label.setStyleSheet("color: #FF9800;")
        else:
            # Critical temperature - Red
            style += """
            QProgressBar::chunk {
                background-color: #F44336;
                border-radius: 2px;
            }
            """
            self.temp_label.setStyleSheet("color: #F44336;")

        self.temp_bar.setStyleSheet(style)
