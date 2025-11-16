#!/usr/bin/env python
"""
MDT Piezo Controller GUI

PyQt5 GUI for controlling MDT693A/B and MDT694B piezo voltage controllers.
Follows the same architecture as the existing motor controller GUI.
"""

import sys
import json
from pathlib import Path
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGridLayout, QLabel, QComboBox, QPushButton, QSlider, QDoubleSpinBox,
    QGroupBox, QCheckBox, QTextEdit, QTabWidget, QMessageBox, QProgressBar
)
from PyQt5.QtCore import QTimer, Qt, pyqtSignal
from PyQt5.QtGui import QFont, QColor, QPalette

from mdt_controller import HighLevelMDTController, discover_mdt_devices


class AxisControlWidget(QWidget):
    """Widget for controlling a single axis with slider and spinbox"""
    
    voltageChanged = pyqtSignal(str, float)  # axis, voltage
    
    def __init__(self, axis_name, min_voltage=0.0, max_voltage=150.0, safe_max=100.0):
        super().__init__()
        self.axis_name = axis_name
        self.min_voltage = min_voltage
        self.max_voltage = max_voltage
        self.safe_max = safe_max
        self.updating = False
        
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Axis label
        label = QLabel(f"{self.axis_name}-Axis Voltage")
        label.setFont(QFont("Arial", 10, QFont.Bold))
        layout.addWidget(label)
        
        # Current voltage display
        self.current_label = QLabel("Current: --- V")
        self.current_label.setStyleSheet("color: blue;")
        layout.addWidget(self.current_label)
        
        # Target voltage controls
        control_layout = QHBoxLayout()
        
        # Slider
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setMaximum(int(self.max_voltage * 10))  # 0.1V resolution
        self.slider.setValue(0)
        self.slider.setTickPosition(QSlider.TicksBelow)
        self.slider.setTickInterval(int(self.max_voltage))
        self.slider.valueChanged.connect(self.on_slider_changed)
        control_layout.addWidget(self.slider)
        
        # Spinbox
        self.spinbox = QDoubleSpinBox()
        self.spinbox.setMinimum(self.min_voltage)
        self.spinbox.setMaximum(self.max_voltage)
        self.spinbox.setValue(0.0)
        self.spinbox.setSingleStep(1.0)
        self.spinbox.setDecimals(2)
        self.spinbox.setSuffix(" V")
        self.spinbox.valueChanged.connect(self.on_spinbox_changed)
        control_layout.addWidget(self.spinbox)
        
        layout.addLayout(control_layout)
        
        # Set button
        self.set_button = QPushButton(f"Set {self.axis_name}")
        self.set_button.clicked.connect(self.on_set_clicked)
        layout.addWidget(self.set_button)
        
        self.setLayout(layout)
    
    def on_slider_changed(self, value):
        if not self.updating:
            self.updating = True
            voltage = value / 10.0
            self.spinbox.setValue(voltage)
            self.updating = False
    
    def on_spinbox_changed(self, value):
        if not self.updating:
            self.updating = True
            self.slider.setValue(int(value * 10))
            self.updating = False
    
    def on_set_clicked(self):
        voltage = self.spinbox.value()
        self.voltageChanged.emit(self.axis_name, voltage)
    
    def update_current_voltage(self, voltage):
        """Update the current voltage display"""
        if voltage is not None:
            self.current_label.setText(f"Current: {voltage:.2f} V")
            self.current_label.setStyleSheet("color: blue;")
        else:
            self.current_label.setText("Current: --- V")
            self.current_label.setStyleSheet("color: gray;")
    
    def set_target_voltage(self, voltage):
        """Set the target voltage (slider and spinbox)"""
        self.updating = True
        self.spinbox.setValue(voltage)
        self.slider.setValue(int(voltage * 10))
        self.updating = False
    
    def set_enabled(self, enabled):
        """Enable/disable all controls"""
        self.slider.setEnabled(enabled)
        self.spinbox.setEnabled(enabled)
        self.set_button.setEnabled(enabled)


class MDTControlGUI(QMainWindow):
    """Main GUI for MDT piezo controller"""
    
    def __init__(self):
        super().__init__()
        self.controller = None
        self.device_list = []
        self.axis_widgets = {}
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_voltage_displays)
        
        self.init_ui()
        self.discover_devices()
    
    def init_ui(self):
        self.setWindowTitle("MDT Piezo Controller")
        self.setGeometry(100, 100, 800, 600)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Device selection group
        device_group = QGroupBox("Device Selection")
        device_layout = QHBoxLayout()
        
        device_layout.addWidget(QLabel("Device:"))
        self.device_combo = QComboBox()
        self.device_combo.currentIndexChanged.connect(self.on_device_changed)
        device_layout.addWidget(self.device_combo)
        
        self.refresh_button = QPushButton("Refresh Devices")
        self.refresh_button.clicked.connect(self.discover_devices)
        device_layout.addWidget(self.refresh_button)
        
        self.connect_button = QPushButton("Connect")
        self.connect_button.clicked.connect(self.toggle_connection)
        device_layout.addWidget(self.connect_button)
        
        device_group.setLayout(device_layout)
        main_layout.addWidget(device_group)
        
        # Connection status
        self.status_label = QLabel("Status: Disconnected")
        self.status_label.setStyleSheet("color: red; font-weight: bold;")
        main_layout.addWidget(self.status_label)
        
        # Device info
        self.info_label = QLabel("No device selected")
        main_layout.addWidget(self.info_label)
        
        # Tab widget for different control modes
        self.tab_widget = QTabWidget()
        
        # Voltage control tab
        self.voltage_tab = QWidget()
        self.init_voltage_tab()
        self.tab_widget.addTab(self.voltage_tab, "Voltage Control")
        
        # Advanced tab
        self.advanced_tab = QWidget()
        self.init_advanced_tab()
        self.tab_widget.addTab(self.advanced_tab, "Advanced")
        
        main_layout.addWidget(self.tab_widget)
        
        # Log display
        log_group = QGroupBox("Log")
        log_layout = QVBoxLayout()
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(150)
        log_layout.addWidget(self.log_text)
        log_group.setLayout(log_layout)
        main_layout.addWidget(log_group)
        
        self.log("MDT Control GUI initialized")
    
    def init_voltage_tab(self):
        """Initialize the voltage control tab"""
        layout = QVBoxLayout()
        
        # Axis controls container
        self.axis_container = QWidget()
        self.axis_layout = QGridLayout()
        self.axis_container.setLayout(self.axis_layout)
        layout.addWidget(self.axis_container)
        
        # Control buttons
        button_layout = QHBoxLayout()
        
        self.zero_button = QPushButton("Zero All Axes")
        self.zero_button.clicked.connect(self.zero_all_axes)
        self.zero_button.setEnabled(False)
        button_layout.addWidget(self.zero_button)
        
        self.safety_checkbox = QCheckBox("Safety Limits Enabled")
        self.safety_checkbox.setChecked(True)
        self.safety_checkbox.stateChanged.connect(self.on_safety_changed)
        button_layout.addWidget(self.safety_checkbox)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        # Quick set buttons
        quick_group = QGroupBox("Quick Set")
        quick_layout = QHBoxLayout()
        
        for voltage in [10, 25, 50, 75]:
            btn = QPushButton(f"{voltage}V")
            btn.clicked.connect(lambda checked, v=voltage: self.quick_set_all(v))
            quick_layout.addWidget(btn)
        
        quick_group.setLayout(quick_layout)
        layout.addWidget(quick_group)
        
        layout.addStretch()
        self.voltage_tab.setLayout(layout)
    
    def init_advanced_tab(self):
        """Initialize the advanced features tab"""
        layout = QVBoxLayout()
        
        # Scan control
        scan_group = QGroupBox("Axis Scan")
        scan_layout = QGridLayout()
        
        scan_layout.addWidget(QLabel("Axis:"), 0, 0)
        self.scan_axis_combo = QComboBox()
        scan_layout.addWidget(self.scan_axis_combo, 0, 1)
        
        scan_layout.addWidget(QLabel("Start (V):"), 1, 0)
        self.scan_start_spin = QDoubleSpinBox()
        self.scan_start_spin.setRange(0, 150)
        self.scan_start_spin.setValue(0)
        scan_layout.addWidget(self.scan_start_spin, 1, 1)
        
        scan_layout.addWidget(QLabel("End (V):"), 2, 0)
        self.scan_end_spin = QDoubleSpinBox()
        self.scan_end_spin.setRange(0, 150)
        self.scan_end_spin.setValue(50)
        scan_layout.addWidget(self.scan_end_spin, 2, 1)
        
        scan_layout.addWidget(QLabel("Steps:"), 3, 0)
        self.scan_steps_spin = QDoubleSpinBox()
        self.scan_steps_spin.setRange(2, 1000)
        self.scan_steps_spin.setValue(21)
        self.scan_steps_spin.setDecimals(0)
        scan_layout.addWidget(self.scan_steps_spin, 3, 1)
        
        scan_layout.addWidget(QLabel("Step Time (s):"), 4, 0)
        self.scan_time_spin = QDoubleSpinBox()
        self.scan_time_spin.setRange(0.01, 10)
        self.scan_time_spin.setValue(0.1)
        self.scan_time_spin.setSingleStep(0.1)
        scan_layout.addWidget(self.scan_time_spin, 4, 1)
        
        self.scan_button = QPushButton("Run Scan")
        self.scan_button.clicked.connect(self.run_scan)
        self.scan_button.setEnabled(False)
        scan_layout.addWidget(self.scan_button, 5, 0, 1, 2)
        
        self.scan_progress = QProgressBar()
        scan_layout.addWidget(self.scan_progress, 6, 0, 1, 2)
        
        scan_group.setLayout(scan_layout)
        layout.addWidget(scan_group)
        
        # Device limits display
        limits_group = QGroupBox("Device Limits")
        self.limits_label = QLabel("Connect to device to view limits")
        limits_layout = QVBoxLayout()
        limits_layout.addWidget(self.limits_label)
        limits_group.setLayout(limits_layout)
        layout.addWidget(limits_group)
        
        layout.addStretch()
        self.advanced_tab.setLayout(layout)
    
    def discover_devices(self):
        """Discover available MDT devices"""
        self.log("Discovering MDT devices...")
        try:
            self.device_list = discover_mdt_devices()
            self.device_combo.clear()
            
            if not self.device_list:
                self.log("No MDT devices found")
                QMessageBox.warning(self, "No Devices", "No MDT devices found. Check connections.")
                return
            
            for device in self.device_list:
                label = f"{device.get('Model', 'Unknown')} - {device['Device']}"
                if device.get('Serial Number'):
                    label += f" (SN: {device['Serial Number']})"
                self.device_combo.addItem(label)
            
            self.log(f"Found {len(self.device_list)} devices")
        except Exception as e:
            self.log(f"Error discovering devices: {e}")
            QMessageBox.critical(self, "Error", f"Failed to discover devices:\n{e}")
    
    def on_device_changed(self, index):
        """Handle device selection change"""
        if index < 0 or index >= len(self.device_list):
            return
        
        device = self.device_list[index]
        model = device.get('Model', 'Unknown')
        port = device['Device']
        
        info = f"Model: {model} | Port: {port}"
        if device.get('Serial Number'):
            info += f" | SN: {device['Serial Number']}"
        
        self.info_label.setText(info)
    
    def toggle_connection(self):
        """Connect or disconnect from the selected device"""
        if self.controller and self.controller.is_connected():
            self.disconnect_device()
        else:
            self.connect_device()
    
    def connect_device(self):
        """Connect to the selected device"""
        index = self.device_combo.currentIndex()
        if index < 0:
            QMessageBox.warning(self, "No Device", "Please select a device first")
            return
        
        device = self.device_list[index]
        port = device['Device']
        model = device.get('Model', 'Unknown')
        
        self.log(f"Connecting to {model} on {port}...")
        
        try:
            self.controller = HighLevelMDTController(port=port, model=model, auto_discover=False)
            
            if not self.controller.is_connected():
                raise Exception("Failed to connect to device")
            
            # Update UI
            self.status_label.setText(f"Status: Connected to {model}")
            self.status_label.setStyleSheet("color: green; font-weight: bold;")
            self.connect_button.setText("Disconnect")
            self.zero_button.setEnabled(True)
            self.scan_button.setEnabled(True)
            
            # Create axis controls based on device
            self.create_axis_controls()
            
            # Update limits display
            self.update_limits_display()
            
            # Start monitoring
            self.update_timer.start(500)  # Update every 500ms
            
            self.log(f"Connected successfully to {model}")
            
        except Exception as e:
            self.log(f"Connection error: {e}")
            QMessageBox.critical(self, "Connection Error", f"Failed to connect:\n{e}")
            self.controller = None
    
    def disconnect_device(self):
        """Disconnect from the current device"""
        if self.controller:
            self.log("Disconnecting...")
            self.update_timer.stop()
            self.controller.disconnect()
            self.controller = None
            
            # Update UI
            self.status_label.setText("Status: Disconnected")
            self.status_label.setStyleSheet("color: red; font-weight: bold;")
            self.connect_button.setText("Connect")
            self.zero_button.setEnabled(False)
            self.scan_button.setEnabled(False)
            
            # Clear axis controls
            self.clear_axis_controls()
            
            self.log("Disconnected")
    
    def create_axis_controls(self):
        """Create axis control widgets based on device capabilities"""
        self.clear_axis_controls()
        
        if not self.controller:
            return
        
        axes = self.controller.controller.axes
        
        # Create controls for each axis
        for i, axis in enumerate(axes):
            limits = self.controller.voltage_limits.get(axis, {})
            min_v = limits.get('min', 0.0)
            max_v = limits.get('max', 150.0)
            safe_max = limits.get('safe_max', 100.0)
            
            widget = AxisControlWidget(axis, min_v, max_v, safe_max)
            widget.voltageChanged.connect(self.set_axis_voltage)
            
            row = i // 3
            col = i % 3
            self.axis_layout.addWidget(widget, row, col)
            self.axis_widgets[axis] = widget
        
        # Update scan axis options
        self.scan_axis_combo.clear()
        self.scan_axis_combo.addItems(axes)
    
    def clear_axis_controls(self):
        """Clear all axis control widgets"""
        for widget in self.axis_widgets.values():
            widget.deleteLater()
        self.axis_widgets.clear()
        
        # Clear layout
        while self.axis_layout.count():
            item = self.axis_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
    
    def set_axis_voltage(self, axis, voltage):
        """Set voltage for a specific axis"""
        if not self.controller:
            return
        
        force = not self.safety_checkbox.isChecked()
        self.log(f"Setting {axis}-axis to {voltage:.2f}V...")
        
        try:
            success = self.controller.set_voltage_safe(axis, voltage, force=force)
            if success:
                self.log(f"✓ {axis}-axis set to {voltage:.2f}V")
            else:
                self.log(f"✗ Failed to set {axis}-axis voltage")
                QMessageBox.warning(self, "Set Voltage Failed", 
                                  f"Failed to set {axis}-axis to {voltage:.2f}V")
        except Exception as e:
            self.log(f"Error setting voltage: {e}")
            QMessageBox.critical(self, "Error", f"Error setting voltage:\n{e}")
    
    def zero_all_axes(self):
        """Set all axes to 0V"""
        if not self.controller:
            return
        
        reply = QMessageBox.question(self, "Confirm Zero", 
                                    "Set all axes to 0V?",
                                    QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            self.log("Zeroing all axes...")
            try:
                success = self.controller.zero_all_axes()
                if success:
                    self.log("✓ All axes set to 0V")
                    # Update displays
                    for widget in self.axis_widgets.values():
                        widget.set_target_voltage(0.0)
                else:
                    self.log("✗ Failed to zero all axes")
            except Exception as e:
                self.log(f"Error zeroing axes: {e}")
                QMessageBox.critical(self, "Error", f"Error zeroing axes:\n{e}")
    
    def quick_set_all(self, voltage):
        """Quick set all axes to the same voltage"""
        if not self.controller:
            return
        
        axes = self.controller.controller.axes
        voltages = {axis: voltage for axis in axes}
        
        force = not self.safety_checkbox.isChecked()
        self.log(f"Setting all axes to {voltage}V...")
        
        try:
            success = self.controller.set_all_voltages_safe(voltages, force=force)
            if success:
                self.log(f"✓ All axes set to {voltage}V")
                # Update displays
                for widget in self.axis_widgets.values():
                    widget.set_target_voltage(voltage)
            else:
                self.log(f"✗ Failed to set voltages")
        except Exception as e:
            self.log(f"Error setting voltages: {e}")
            QMessageBox.critical(self, "Error", f"Error setting voltages:\n{e}")
    
    def run_scan(self):
        """Run a voltage scan on the selected axis"""
        if not self.controller:
            return
        
        axis = self.scan_axis_combo.currentText()
        start = self.scan_start_spin.value()
        end = self.scan_end_spin.value()
        steps = int(self.scan_steps_spin.value())
        step_time = self.scan_time_spin.value()
        
        self.log(f"Starting scan: {axis}-axis from {start}V to {end}V in {steps} steps")
        self.scan_button.setEnabled(False)
        self.scan_progress.setValue(0)
        
        try:
            results = self.controller.scan_axis(axis, start, end, steps, step_time)
            
            self.scan_progress.setValue(100)
            self.log(f"✓ Scan complete: {len(results)} points recorded")
            
            # Could add plotting or data export here
            
        except Exception as e:
            self.log(f"Scan error: {e}")
            QMessageBox.critical(self, "Scan Error", f"Scan failed:\n{e}")
        finally:
            self.scan_button.setEnabled(True)
    
    def update_voltage_displays(self):
        """Update current voltage displays from device"""
        if not self.controller or not self.controller.is_connected():
            return
        
        try:
            voltages = self.controller.controller.get_all_voltages()
            for axis, voltage in voltages.items():
                if axis in self.axis_widgets:
                    self.axis_widgets[axis].update_current_voltage(voltage)
        except Exception as e:
            self.log(f"Error reading voltages: {e}")
    
    def update_limits_display(self):
        """Update the limits display"""
        if not self.controller:
            return
        
        text = "Voltage Limits:\n"
        for axis, limits in self.controller.voltage_limits.items():
            text += f"{axis}-axis: {limits['min']:.1f}V - {limits['max']:.1f}V "
            text += f"(safe: {limits['safe_max']:.1f}V)\n"
        
        self.limits_label.setText(text)
    
    def on_safety_changed(self, state):
        """Handle safety checkbox state change"""
        enabled = (state == Qt.Checked)
        if self.controller:
            self.controller.enable_safety(enabled)
        self.log(f"Safety limits {'enabled' if enabled else 'disabled'}")
    
    def log(self, message):
        """Add a message to the log"""
        self.log_text.append(message)
        # Auto-scroll to bottom
        scrollbar = self.log_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def closeEvent(self, event):
        """Handle window close event"""
        if self.controller:
            self.disconnect_device()
        event.accept()


def main():
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    gui = MDTControlGUI()
    gui.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
