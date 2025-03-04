from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
                               QLabel, QProgressBar, QScrollArea, QSizePolicy)
from PySide6.QtCore import Qt, Slot
from src.ui.sensor_widget import TemperatureSensorWidget


class DashboardWidget(QWidget):
    def __init__(self, hardware_monitor):
        super().__init__()

        self.hardware_monitor = hardware_monitor

        # Main layout
        main_layout = QVBoxLayout(self)

        # Create scroll area for the content
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)

        # Scroll content widget
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)

        # CPU section
        self.cpu_group = QGroupBox("CPU")
        cpu_layout = QVBoxLayout(self.cpu_group)

        self.cpu_name = QLabel("Loading CPU info...")
        self.cpu_usage = QProgressBar()
        self.cpu_usage.setRange(0, 100)

        # CPU temperature widgets container
        self.cpu_temp_layout = QVBoxLayout()

        cpu_layout.addWidget(self.cpu_name)
        cpu_layout.addWidget(QLabel("CPU Utilization:"))
        cpu_layout.addWidget(self.cpu_usage)
        cpu_layout.addWidget(QLabel("CPU Temperatures:"))
        cpu_layout.addLayout(self.cpu_temp_layout)

        # GPU section
        self.gpu_group = QGroupBox("GPU")
        gpu_layout = QVBoxLayout(self.gpu_group)

        self.gpu_name = QLabel("Detecting GPU...")
        self.gpu_temp_layout = QVBoxLayout()

        gpu_layout.addWidget(self.gpu_name)
        gpu_layout.addWidget(QLabel("GPU Temperatures:"))
        gpu_layout.addLayout(self.gpu_temp_layout)

        # Motherboard section
        self.mb_group = QGroupBox("Motherboard")
        mb_layout = QVBoxLayout(self.mb_group)

        self.mb_name = QLabel("Detecting motherboard...")
        self.mb_temp_layout = QVBoxLayout()

        mb_layout.addWidget(self.mb_name)
        mb_layout.addWidget(QLabel("Motherboard Sensors:"))
        mb_layout.addLayout(self.mb_temp_layout)

        # Add all groups to scroll layout
        scroll_layout.addWidget(self.cpu_group)
        scroll_layout.addWidget(self.gpu_group)
        scroll_layout.addWidget(self.mb_group)
        scroll_layout.addStretch()

        # Set the scroll content and add to main layout
        scroll_area.setWidget(scroll_content)
        main_layout.addWidget(scroll_area)

        # Connect signals
        self.hardware_monitor.data_updated.connect(self.update_dashboard)

    @Slot(dict)
    def update_dashboard(self, data):
        # Handle partial updates - check which sections are included in the data
        if 'cpu' in data:
            cpu_data = data['cpu']

            # Only update what's available in this update
            if 'name' in cpu_data:
                self.cpu_name.setText(
                    f"{cpu_data['name']} ({cpu_data.get('core_count', '?')} cores, {cpu_data.get('thread_count', '?')} threads)")

            if 'overall_usage' in cpu_data:
                self.cpu_usage.setValue(int(cpu_data['overall_usage']))

            if 'temperature' in cpu_data:
                # Clear and update CPU temperature widgets
                self._clear_layout(self.cpu_temp_layout)

                for sensor_name, temp in cpu_data['temperature'].items():
                    if temp is not None:
                        sensor_widget = TemperatureSensorWidget(sensor_name, temp)
                        self.cpu_temp_layout.addWidget(sensor_widget)

        if 'gpu' in data:
            gpu_data = data['gpu']
            if gpu_data['available']:
                if 'devices' in gpu_data and gpu_data['devices']:
                    self.gpu_name.setText(gpu_data['devices'][0]['name'])
                else:
                    self.gpu_name.setText("GPU detected")

                # Clear and update GPU temperature widgets
                self._clear_layout(self.gpu_temp_layout)

                # Add message about Intel GPU if applicable
                if 'message' in gpu_data:
                    message_label = QLabel(gpu_data['message'])
                    message_label.setStyleSheet("color: #FFA500;")  # Orange text
                    self.gpu_temp_layout.addWidget(message_label)

                # Show GPU utilization info if temperature is unavailable
                if 'utilization' in gpu_data:
                    for metric_name, value in gpu_data['utilization'].items():
                        label = QLabel(f"{metric_name.replace('_', ' ').title()}: {value}")
                        self.gpu_temp_layout.addWidget(label)

                if 'temperature' in gpu_data:
                    for sensor_name, temp in gpu_data['temperature'].items():
                        if temp is not None:
                            sensor_widget = TemperatureSensorWidget(sensor_name, temp)
                            self.gpu_temp_layout.addWidget(sensor_widget)
                        else:
                            label = QLabel(f"{sensor_name}: Not available")
                            label.setStyleSheet("color: #888888;")  # Gray text
                            self.gpu_temp_layout.addWidget(label)
            else:
                self.gpu_name.setText("No dedicated GPU detected")

        if 'motherboard' in data:
            mb_data = data['motherboard']
            if 'manufacturer' in mb_data and 'model' in mb_data:
                model_name = mb_data.get('model_name', mb_data['model'])
                self.mb_name.setText(f"{mb_data['manufacturer']} {model_name}")
            else:
                self.mb_name.setText("Motherboard information unavailable")

            # Clear and update motherboard temperature widgets
            self._clear_layout(self.mb_temp_layout)

            # Show message if present
            if 'message' in mb_data:
                message_label = QLabel(mb_data['message'])
                message_label.setStyleSheet("color: #FFA500;")  # Orange text
                self.mb_temp_layout.addWidget(message_label)

            # Show battery info if present
            if 'battery' in mb_data:
                for metric, value in mb_data['battery'].items():
                    label = QLabel(f"Battery {metric.replace('_', ' ').title()}: {value}")
                    self.mb_temp_layout.addWidget(label)

            # Show sensors if available
            if 'sensors' in mb_data:
                if mb_data['sensors']:
                    for sensor_name, sensor_data in mb_data['sensors'].items():
                        if isinstance(sensor_data, dict) and 'value' in sensor_data:
                            temp = sensor_data['value']
                        else:
                            temp = sensor_data

                        if temp is not None:
                            sensor_widget = TemperatureSensorWidget(sensor_name, temp)
                            self.mb_temp_layout.addWidget(sensor_widget)
                else:
                    no_sensors_label = QLabel("No temperature sensors detected")
                    self.mb_temp_layout.addWidget(no_sensors_label)

            # Show power info if present
            if 'power' in mb_data:
                for metric, value in mb_data['power'].items():
                    label = QLabel(f"{metric}: {value}")
                    self.mb_temp_layout.addWidget(label)

    def _clear_layout(self, layout):
        """Clear all widgets from a layout"""
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
