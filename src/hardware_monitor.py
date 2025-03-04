import psutil
import platform
import cpuinfo
from PySide6.QtCore import QObject, Signal, QTimer, QThread, QMutex
import time
import subprocess
import threading


class SensorWorker(QThread):
    """Worker thread to handle sensor data collection without blocking UI"""
    data_ready = Signal(dict)

    def __init__(self):
        super().__init__()
        self.mutex = QMutex()
        self.abort = False
        self.interval = 1000  # ms

    def run(self):
        while not self.abort:
            # Collect data in background thread
            data = self.collect_data()
            self.data_ready.emit(data)
            time.sleep(self.interval / 1000)

    def stop(self):
        self.mutex.lock()
        self.abort = True
        self.mutex.unlock()
        self.wait()

    def collect_data(self):
        """Collect all sensor data - runs in background thread"""
        data = {
            "timestamp": time.time(),
            "cpu": self.get_cpu_info(),
            "gpu": self.get_gpu_info(),
            "motherboard": self.get_motherboard_info()
        }
        return data

    def get_cpu_info(self):
        """Get CPU information safely"""
        try:
            cpu_info = cpuinfo.get_cpu_info()
            cpu_data = {
                "name": cpu_info.get('brand_raw', "Unknown CPU"),
                "usage_percent": psutil.cpu_percent(interval=None, percpu=True),
                "overall_usage": psutil.cpu_percent(interval=None),
                "core_count": psutil.cpu_count(logical=False),
                "thread_count": psutil.cpu_count(logical=True)
            }

            # Get CPU temperature with timeout safety
            try:
                cpu_data["temperature"] = self.get_cpu_temperature()
            except:
                cpu_data["temperature"] = {"CPU": None}

            # Get CPU frequency if available
            try:
                cpu_data["frequency"] = psutil.cpu_freq(percpu=True)
            except:
                cpu_data["frequency"] = None

            return cpu_data
        except Exception as e:
            print(f"Error getting CPU info: {e}")
            return {"name": "Error reading CPU info", "overall_usage": 0}

    def get_cpu_temperature(self):
        """Get CPU temperature safely with fallbacks"""
        temps = {"CPU": None}
        if platform.system() == "Windows":
            try:
                import wmi
                w = wmi.WMI(namespace=r"root\OpenHardwareMonitor")
                temperature_infos = w.Sensor()

                # Collect all CPU temperatures
                cpu_temps = {}
                for sensor in temperature_infos:
                    if sensor.SensorType == 'Temperature' and 'CPU' in sensor.Name:
                        # Handle multiple cores
                        cpu_temps[sensor.Name] = float(sensor.Value)
                if cpu_temps:
                    return cpu_temps
                else:
                    temps["error"] = "OpenHardwareMonitor not detected. Please install and run it first."
                    return temps
            except Exception as e:
                print(f"Error accessing CPU temperature on Windows: {e}")

        elif platform.system() == "Darwin":  # macOS
            try:
                # Try osx-cpu-temp first - most reliable on macOS
                output = subprocess.check_output(["osx-cpu-temp"], text=True, timeout=1)
                if "°C" in output:
                    temp_value = float(output.replace("°C", "").strip())
                    temps["CPU"] = temp_value
                    return temps
            except (subprocess.SubprocessError, FileNotFoundError, subprocess.TimeoutExpired):
                pass

            # Fallback to sysctl
            try:
                output = subprocess.check_output(["sysctl", "-a"], text=True, timeout=1)
                for line in output.splitlines():
                    if "machdep.xcpm.cpu_thermal_level" in line:
                        # This provides thermal level, not exact temperature
                        thermal_level = int(line.split(":")[-1].strip())
                        # Convert thermal level to estimated temperature (approximation)
                        estimated_temp = 45 + (thermal_level * 10)
                        temps["CPU"] = estimated_temp
                        temps["note"] = "Estimated from thermal level"
                        return temps
            except:
                pass

        return temps

    def get_gpu_info(self):
        """Get GPU information safely for Mac"""
        gpu_data = {"available": False}

        if platform.system() == "Darwin":  # macOS
            try:
                # Just get basic GPU info without trying for temperatures
                output = subprocess.check_output(["system_profiler", "SPDisplaysDataType"],
                                                 text=True, timeout=2)

                if output:
                    gpu_data["available"] = True
                    gpu_data["devices"] = []

                    # Basic parsing - find GPU name
                    current_gpu = {}
                    for line in output.splitlines():
                        line = line.strip()
                        if "Chipset Model:" in line:
                            current_gpu = {"name": line.split("Chipset Model:")[1].strip()}
                            gpu_data["devices"].append(current_gpu)
                        elif "VRAM" in line and current_gpu:
                            current_gpu["vram"] = line.split(":")[-1].strip()

                    # For Intel integrated GPU, provide basic info
                    if any("Intel" in device.get("name", "") for device in gpu_data.get("devices", [])):
                        gpu_data["message"] = "Temperature data unavailable for Intel integrated GPU"
                        gpu_data["temperature"] = {"GPU": None}

                        # Add some basic GPU utilization info
                        gpu_data["utilization"] = {"GPU Load": "Unknown - Limited API access"}
            except:
                pass

        return gpu_data

    def get_motherboard_info(self):
        """Get motherboard/system information safely for Mac"""
        mb_data = {"sensors": {}}

        if platform.system() == "Darwin":
            try:
                # Get Mac model info - always works
                output = subprocess.check_output(["sysctl", "hw.model"], text=True, timeout=1)
                if output:
                    mac_model = output.split(":")[-1].strip()
                    mb_data["model"] = mac_model
                    mb_data["manufacturer"] = "Apple"

                    # For MacBook Pro, add more descriptive model name
                    if "MacBookPro16,2" in mac_model:
                        mb_data["model_name"] = "MacBook Pro (13-inch, 2020, Intel)"
            except:
                pass

            # Get battery information as alternative data point
            try:
                batt_info = subprocess.check_output(["pmset", "-g", "batt"], text=True, timeout=1)
                mb_data["battery"] = {}

                for line in batt_info.splitlines():
                    if "%" in line:
                        # Example: "Now drawing from 'Battery Power'" -  (id=) 45%; discharging; 2:32 remaining
                        parts = line.split(";")
                        if len(parts) >= 2:
                            # Get battery percentage
                            pct_part = parts[0].split("%")[0].strip()
                            pct = pct_part.split()[-1].strip()
                            mb_data["battery"]["charge"] = f"{pct}%"

                            # Get charging status
                            status = parts[1].strip()
                            mb_data["battery"]["status"] = status

                            # Get remaining time if available
                            if len(parts) >= 3:
                                remaining = parts[2].strip()
                                mb_data["battery"]["remaining"] = remaining
            except:
                pass

            # Instead of trying to get actual temps, add a message about limited access
            mb_data["message"] = "Limited sensor access on MacOS. System health metrics shown instead."
            # Try different power/thermal metrics that might be available
            try:
                power_metrics = [
                    "machdep.xcpm.pkg_power",  # Intel Macs
                    "machdep.xcpm.cpu_thermal_level",  # Alternative thermal indicator
                    "hw.sensors.cpu0.temp0"  # Another possible temperature source
                ]

                for metric in power_metrics:
                    try:
                        output = subprocess.check_output(["sysctl", metric], text=True, timeout=1,
                                                         stderr=subprocess.DEVNULL)
                        if output:
                            value = float(output.split(":")[-1].strip())
                            mb_data["power"] = {"System Power": f"{value:.2f} W" if "power" in metric else f"{value:.1f}"}
                            break  # Found a working metric, stop trying others
                    except subprocess.CalledProcessError:
                        # This specific metric doesn't exist, try the next one
                        continue
                    except ValueError:
                        # Couldn't convert to float, try the next one
                        continue
            except:
                # If all attempts fail, just continue without power metrics
                pass
        return mb_data


class HardwareMonitor(QObject):
    data_updated = Signal(dict)

    def __init__(self, update_interval=1000):
        super().__init__()
        self.update_interval = update_interval

        # Create background worker thread for sensor data
        self.worker = SensorWorker()
        self.worker.interval = update_interval
        self.worker.data_ready.connect(self.on_data_ready)

    def start(self):
        self.worker.start()

    def stop(self):
        self.worker.stop()

    def on_data_ready(self, data):
        # This runs in the main thread, safe to emit signals
        self.data_updated.emit(data)

    def update_data(self):
        # This is now a no-op as data collection happens in the background thread
        pass

