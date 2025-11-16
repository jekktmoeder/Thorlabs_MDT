import re

# Read original GUI file
with open("MDTControlGUI.py", "r", encoding="utf-8") as f:
    content = f.read()

# Major refactoring needed - will rewrite key sections

# 1. Replace __init__ to use controllers dict
old_init = '''        self.controller = None
        self.monitoring_active = False
        
        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)'''

new_init = '''        self.controllers = {}  # port -> HighLevelMDTController
        self.monitoring_active = False
        
        # Create main widget with tabs
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        
        # Create tab widget for per-device control
        self.device_tabs = QTabWidget()
        layout.addWidget(self.device_tabs)'''

content = content.replace(old_init, new_init)

# 2. Fix quick-set voltages
content = content.replace("[10, 25, 50, 75]", "[10, 25, 50, 75, 100, 150]")

# 3. Update connect_device to create tabs
old_connect = '''            self.controller = HighLevelMDTController()
            if self.controller.connect(port):
                msg = f"Connected to {info['Model']} on {port}"
                if info.get('Serial Number'):
                    msg += f" (S/N: {info['Serial Number']})"
                self.log(msg)
                
                # Enable controls
                self.setup_controls()
                
                # Start monitoring
                self.start_monitoring()
            else:
                self.log(f"Failed to connect to {info['Model']} on {port}", "ERROR")
                self.controller = None'''

new_connect = '''            controller = HighLevelMDTController()
            if controller.connect(port):
                self.controllers[port] = controller
                
                # Create tab for this device
                device_name = f"{info['Model']} - {port}"
                tab_widget = self.create_device_tab(port, controller)
                self.device_tabs.addTab(tab_widget, device_name)
                
                msg = f"Connected to {info['Model']} on {port}"
                if info.get('Serial Number'):
                    msg += f" (S/N: {info['Serial Number']})"
                self.log(msg)
                
                # Start monitoring if first device
                if not self.monitoring_active:
                    self.start_monitoring()
            else:
                self.log(f"Failed to connect to {info['Model']} on {port}", "ERROR")'''

content = content.replace(old_connect, new_connect)

# 4. Add create_device_tab method before setup_controls
new_method = '''    
    def create_device_tab(self, port: str, controller) -> QWidget:
        """Create control tab for a device"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Device info
        info_group = QGroupBox("Device Information")
        info_layout = QVBoxLayout()
        info_layout.addWidget(QLabel(f"Port: {port}"))
        info_layout.addWidget(QLabel(f"Axes: {', '.join(controller.controller.axes)}"))
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        # Axis controls
        controls_group = QGroupBox("Voltage Control")
        controls_layout = QVBoxLayout()
        
        axis_controls = {}
        for axis in controller.controller.axes:
            axis_widget = AxisControlWidget(axis, controller.voltage_limits[axis])
            axis_widget.voltageChanged.connect(
                lambda v, a=axis, p=port: self.on_voltage_changed(p, a, v)
            )
            controls_layout.addWidget(axis_widget)
            axis_controls[axis] = axis_widget
        
        controls_group.setLayout(controls_layout)
        layout.addWidget(controls_group)
        
        # Quick actions
        actions_group = QGroupBox("Quick Actions")
        actions_layout = QHBoxLayout()
        
        zero_btn = QPushButton("Zero All")
        zero_btn.clicked.connect(lambda: self.zero_all_voltages(port))
        actions_layout.addWidget(zero_btn)
        
        disconnect_btn = QPushButton("Disconnect")
        disconnect_btn.clicked.connect(lambda: self.disconnect_device(port))
        actions_layout.addWidget(disconnect_btn)
        
        actions_group.setLayout(actions_layout)
        layout.addWidget(actions_group)
        
        layout.addStretch()
        
        # Store reference to controls
        tab.axis_controls = axis_controls
        return tab
    
'''

content = content.replace("    def setup_controls(self):", new_method + "    def setup_controls(self):")

# 5. Update disconnect_device to handle specific port
old_disconnect = '''    def disconnect_device(self):
        """Disconnect from device"""
        if self.controller:
            self.stop_monitoring()
            self.controller.disconnect()
            self.controller = None
            
            # Disable controls
            for widget in self.findChildren((QSlider, QDoubleSpinBox, QPushButton)):
                if widget.objectName() != "connect_btn":
                    widget.setEnabled(False)
            
            self.log("Device disconnected")'''

new_disconnect = '''    def disconnect_device(self, port: str = None):
        """Disconnect from device"""
        if port is None:
            # Disconnect all
            ports = list(self.controllers.keys())
            for p in ports:
                self.disconnect_device(p)
            return
        
        if port in self.controllers:
            self.controllers[port].disconnect()
            del self.controllers[port]
            
            # Remove tab
            for i in range(self.device_tabs.count()):
                if port in self.device_tabs.tabText(i):
                    self.device_tabs.removeTab(i)
                    break
            
            self.log(f"Disconnected from {port}")
            
            # Stop monitoring if no devices
            if not self.controllers:
                self.stop_monitoring()'''

content = content.replace(old_disconnect, new_disconnect)

# 6. Add on_voltage_changed handler
new_handler = '''    
    def on_voltage_changed(self, port: str, axis: str, voltage: float):
        """Handle voltage change from axis control"""
        if port not in self.controllers:
            return
        
        controller = self.controllers[port]
        success = controller.set_voltage(axis, voltage)
        
        if not success:
            self.log(f"Warning: {port} {axis} set to {voltage:.2f}V - verification uncertain", "WARNING")
    
'''

content = content.replace("    def zero_all_voltages(self):", new_handler + "    def zero_all_voltages(self, port: str = None):")

# 7. Update zero_all_voltages
old_zero = '''        """Set all voltages to zero"""
        if not self.controller:
            return
        
        for axis in self.controller.controller.axes:
            self.controller.set_voltage(axis, 0.0)
        
        self.log("All voltages set to zero")'''

new_zero = '''        """Set all voltages to zero"""
        if port:
            # Zero specific device
            if port in self.controllers:
                for axis in self.controllers[port].controller.axes:
                    self.controllers[port].set_voltage(axis, 0.0)
                self.log(f"{port}: All voltages set to zero")
        else:
            # Zero all devices
            for port, controller in self.controllers.items():
                for axis in controller.controller.axes:
                    controller.set_voltage(axis, 0.0)
            self.log("All devices: voltages set to zero")'''

content = content.replace(old_zero, new_zero)

# 8. Update update_readings
old_update = '''    def update_readings(self):
        """Update voltage readings from device"""
        if not self.controller or not self.monitoring_active:
            return
        
        try:
            for axis in self.controller.controller.axes:
                voltage = self.controller.get_voltage(axis)
                if voltage is not None:
                    # Update display - find the AxisControlWidget for this axis
                    for widget in self.findChildren(AxisControlWidget):
                        if widget.axis == axis:
                            widget.update_reading(voltage)
                            break
        except Exception as e:
            self.log(f"Error reading voltages: {e}", "ERROR")'''

new_update = '''    def update_readings(self):
        """Update voltage readings from all devices"""
        if not self.controllers or not self.monitoring_active:
            return
        
        try:
            for port, controller in self.controllers.items():
                # Find the tab for this port
                for i in range(self.device_tabs.count()):
                    if port in self.device_tabs.tabText(i):
                        tab = self.device_tabs.widget(i)
                        if hasattr(tab, 'axis_controls'):
                            for axis, widget in tab.axis_controls.items():
                                voltage = controller.get_voltage(axis)
                                if voltage is not None:
                                    widget.update_reading(voltage)
                        break
        except Exception as e:
            self.log(f"Error reading voltages: {e}", "ERROR")'''

content = content.replace(old_update, new_update)

# Write updated file
with open("MDTControlGUI.py", "w", encoding="utf-8") as f:
    f.write(content)

print("MDTControlGUI.py updated successfully")
