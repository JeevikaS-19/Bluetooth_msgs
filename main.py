"""
GUI-based Bluetooth Messenger using Kivy
Provides a simple chat interface for Bluetooth communication
"""

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.properties import StringProperty, ListProperty
from kivy.clock import Clock
from kivy.core.window import Window

import bluetooth
import threading
from datetime import datetime
from auth import AuthManager
from message_manager import MessageManager


class DeviceSelectionScreen(Screen):
    """Screen for selecting Bluetooth device to connect to"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        # Title
        title = Label(
            text='Bluetooth Messenger',
            font_size='24sp',
            size_hint=(1, 0.1),
            bold=True
        )
        self.layout.add_widget(title)
        
        # Instructions
        instructions = Label(
            text='Select a device to start hosting or connect as client',
            font_size='14sp',
            size_hint=(1, 0.1)
        )
        self.layout.add_widget(instructions)
        
        # Scan button
        self.scan_btn = Button(
            text='Scan for Devices',
            size_hint=(1, 0.1),
            background_color=(0.2, 0.6, 1, 1)
        )
        self.scan_btn.bind(on_press=self.scan_devices)
        self.layout.add_widget(self.scan_btn)
        
        # Device list (scrollable)
        self.device_scroll = ScrollView(size_hint=(1, 0.5))
        self.device_list = BoxLayout(orientation='vertical', size_hint_y=None, spacing=5)
        self.device_list.bind(minimum_height=self.device_list.setter('height'))
        self.device_scroll.add_widget(self.device_list)
        self.layout.add_widget(self.device_scroll)
        
        # Status label
        self.status_label = Label(
            text='Tap "Scan for Devices" to begin',
            size_hint=(1, 0.1),
            color=(0.7, 0.7, 0.7, 1)
        )
        self.layout.add_widget(self.status_label)
        
        # Host mode button
        host_btn = Button(
            text='Start as Host (No Connection)',
            size_hint=(1, 0.1),
            background_color=(0.2, 0.8, 0.2, 1)
        )
        host_btn.bind(on_press=self.start_host_mode)
        self.layout.add_widget(host_btn)
        
        self.add_widget(self.layout)
        self.devices = []
    
    def scan_devices(self, instance):
        """Scan for nearby Bluetooth devices"""
        self.scan_btn.disabled = True
        self.status_label.text = 'Scanning for devices...'
        self.device_list.clear_widgets()
        
        # Run scan in background thread
        threading.Thread(target=self._scan_thread, daemon=True).start()
    
    def _scan_thread(self):
        """Background thread for device scanning"""
        try:
            nearby_devices = bluetooth.discover_devices(
                duration=8,
                lookup_names=True,
                flush_cache=True
            )
            
            self.devices = nearby_devices
            Clock.schedule_once(lambda dt: self._update_device_list(nearby_devices))
            
        except Exception as e:
            Clock.schedule_once(lambda dt: self._scan_error(str(e)))
    
    def _update_device_list(self, devices):
        """Update UI with found devices"""
        self.device_list.clear_widgets()
        
        if devices:
            self.status_label.text = f'Found {len(devices)} device(s)'
            
            for addr, name in devices:
                btn = Button(
                    text=f'{name}\n{addr}',
                    size_hint_y=None,
                    height=60,
                    background_color=(0.3, 0.3, 0.3, 1)
                )
                btn.bind(on_press=lambda x, a=addr, n=name: self.device_selected(a, n))
                self.device_list.add_widget(btn)
        else:
            self.status_label.text = 'No devices found. Try scanning again.'
        
        self.scan_btn.disabled = False
    
    def _scan_error(self, error):
        """Handle scanning error"""
        self.status_label.text = f'Error: {error}'
        self.scan_btn.disabled = False
    
    def device_selected(self, addr, name):
        """Handle device selection - connect as client"""
        app = App.get_running_app()
        app.selected_device = (addr, name)
        app.is_host = False
        self.manager.current = 'pin_entry'
    
    def start_host_mode(self, instance):
        """Start as host without connecting to another device"""
        app = App.get_running_app()
        app.is_host = True
        app.start_bluetooth_host()
        self.manager.current = 'chat'


class PinEntryScreen(Screen):
    """Screen for entering PIN to authenticate"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        # Title
        title = Label(
            text='Enter PIN',
            font_size='24sp',
            size_hint=(1, 0.2),
            bold=True
        )
        self.layout.add_widget(title)
        
        # Device info
        self.device_label = Label(
            text='Connecting to device...',
            font_size='14sp',
            size_hint=(1, 0.1)
        )
        self.layout.add_widget(self.device_label)
        
        # PIN input
        self.pin_input = TextInput(
            hint_text='Enter 6-digit PIN',
            multiline=False,
            font_size='20sp',
            size_hint=(1, 0.15),
            input_filter='int',
            max_chars=6
        )
        self.layout.add_widget(self.pin_input)
        
        # Connect button
        connect_btn = Button(
            text='Connect',
            size_hint=(1, 0.15),
            background_color=(0.2, 0.6, 1, 1)
        )
        connect_btn.bind(on_press=self.connect_to_host)
        self.layout.add_widget(connect_btn)
        
        # Status
        self.status_label = Label(
            text='',
            size_hint=(1, 0.2),
            color=(1, 0.3, 0.3, 1)
        )
        self.layout.add_widget(self.status_label)
        
        # Back button
        back_btn = Button(
            text='Back',
            size_hint=(1, 0.1),
            background_color=(0.5, 0.5, 0.5, 1)
        )
        back_btn.bind(on_press=self.go_back)
        self.layout.add_widget(back_btn)
        
        self.add_widget(self.layout)
    
    def on_enter(self):
        """Called when screen is displayed"""
        app = App.get_running_app()
        if hasattr(app, 'selected_device'):
            addr, name = app.selected_device
            self.device_label.text = f'Connecting to: {name}'
    
    def connect_to_host(self, instance):
        """Connect to the host with PIN"""
        pin = self.pin_input.text
        
        if len(pin) != 6:
            self.status_label.text = 'PIN must be 6 digits'
            return
        
        self.status_label.text = 'Connecting...'
        app = App.get_running_app()
        app.pin = pin
        
        # Connect in background
        threading.Thread(target=app.connect_to_host, daemon=True).start()
    
    def go_back(self, instance):
        """Go back to device selection"""
        self.manager.current = 'device_selection'


class ChatScreen(Screen):
    """Main chat screen"""
    
    messages_text = StringProperty('')
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Header
        self.header = Label(
            text='Bluetooth Messenger',
            font_size='18sp',
            size_hint=(1, 0.08),
            bold=True
        )
        self.layout.add_widget(self.header)
        
        # Messages area (scrollable)
        self.message_scroll = ScrollView(size_hint=(1, 0.75))
        self.message_label = Label(
            text='',
            size_hint_y=None,
            markup=True,
            halign='left',
            valign='top'
        )
        self.message_label.bind(
            texture_size=self.message_label.setter('size'),
            text=self.message_label.setter('text_size')
        )
        self.message_scroll.add_widget(self.message_label)
        self.layout.add_widget(self.message_scroll)
        
        # Input area
        input_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.12), spacing=10)
        
        self.message_input = TextInput(
            hint_text='Type a message...',
            multiline=False,
            size_hint=(0.75, 1)
        )
        self.message_input.bind(on_text_validate=self.send_message)
        input_layout.add_widget(self.message_input)
        
        send_btn = Button(
            text='Send',
            size_hint=(0.25, 1),
            background_color=(0.2, 0.6, 1, 1)
        )
        send_btn.bind(on_press=self.send_message)
        input_layout.add_widget(send_btn)
        
        self.layout.add_widget(input_layout)
        
        # Status bar
        self.status_bar = Label(
            text='',
            size_hint=(1, 0.05),
            color=(0.7, 0.7, 0.7, 1),
            font_size='12sp'
        )
        self.layout.add_widget(self.status_bar)
        
        self.add_widget(self.layout)
        
        # Schedule message updates
        Clock.schedule_interval(self.update_messages, 1)
    
    def on_enter(self):
        """Called when screen is displayed"""
        app = App.get_running_app()
        if app.is_host:
            self.header.text = f'Host Mode - PIN: {app.host_pin}'
            self.status_bar.text = 'Waiting for connections...'
        else:
            self.header.text = 'Client Mode'
            self.status_bar.text = 'Connected'
    
    def send_message(self, instance):
        """Send a message"""
        message = self.message_input.text.strip()
        
        if not message:
            return
        
        app = App.get_running_app()
        app.send_message(message)
        
        self.message_input.text = ''
    
    def update_messages(self, dt):
        """Update message display"""
        app = App.get_running_app()
        messages = app.get_messages()
        
        if messages:
            self.message_label.text = '\n'.join([str(msg) for msg in messages])
            # Auto-scroll to bottom
            self.message_scroll.scroll_y = 0


class BluetoothMessengerApp(App):
    """Main application class"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.is_host = False
        self.host_pin = None
        self.selected_device = None
        self.pin = None
        self.message_manager = MessageManager(expiry_minutes=5)
        self.auth = AuthManager()
        self.socket = None
        self.server_socket = None
        self.clients = {}
        self.running = True
    
    def build(self):
        """Build the app UI"""
        Window.clearcolor = (0.1, 0.1, 0.1, 1)
        
        sm = ScreenManager()
        sm.add_widget(DeviceSelectionScreen(name='device_selection'))
        sm.add_widget(PinEntryScreen(name='pin_entry'))
        sm.add_widget(ChatScreen(name='chat'))
        
        return sm
    
    def start_bluetooth_host(self):
        """Start Bluetooth host"""
        self.host_pin = self.auth.generate_pin()
        threading.Thread(target=self._host_thread, daemon=True).start()
    
    def _host_thread(self):
        """Host thread"""
        try:
            self.server_socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
            self.server_socket.bind(("", bluetooth.PORT_ANY))
            self.server_socket.listen(5)
            
            bluetooth.advertise_service(
                self.server_socket,
                "BluetoothMessenger",
                service_id="00001101-0000-1000-8000-00805F9B34FB",
                service_classes=["00001101-0000-1000-8000-00805F9B34FB"],
                profiles=[("00001101-0000-1000-8000-00805F9B34FB", 0x0100)]
            )
            
            while self.running:
                client_socket, client_info = self.server_socket.accept()
                threading.Thread(
                    target=self._handle_client,
                    args=(client_socket, client_info),
                    daemon=True
                ).start()
                
        except Exception as e:
            print(f"Host error: {e}")
    
    def _handle_client(self, client_socket, client_info):
        """Handle client connection"""
        try:
            # Send auth request
            client_socket.send("AUTH_REQUEST".encode('utf-8'))
            
            # Receive PIN
            received_pin = client_socket.recv(1024).decode('utf-8')
            
            if self.auth.validate_pin(received_pin):
                client_socket.send("AUTH_SUCCESS".encode('utf-8'))
                self.clients[client_socket] = f"peer{len(self.clients) + 1}"
                
                # Receive messages
                while self.running:
                    data = client_socket.recv(1024)
                    if not data:
                        break
                    
                    message = data.decode('utf-8')
                    sender = self.clients[client_socket]
                    self.message_manager.add_message(sender, message)
                    
                    # Broadcast to other clients
                    for cs in self.clients:
                        if cs != client_socket:
                            try:
                                cs.send(f"{sender}: {message}".encode('utf-8'))
                            except:
                                pass
            else:
                client_socket.send("AUTH_FAILED".encode('utf-8'))
                client_socket.close()
                
        except Exception as e:
            print(f"Client handler error: {e}")
    
    def connect_to_host(self):
        """Connect to host as client"""
        try:
            addr, name = self.selected_device
            
            # Find service
            service_matches = bluetooth.find_service(
                name="BluetoothMessenger",
                address=addr
            )
            
            if not service_matches:
                Clock.schedule_once(lambda dt: self._connection_failed("Service not found"))
                return
            
            port = service_matches[0]["port"]
            
            # Connect
            self.socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
            self.socket.connect((addr, port))
            
            # Authenticate
            data = self.socket.recv(1024).decode('utf-8')
            if data == "AUTH_REQUEST":
                self.socket.send(self.pin.encode('utf-8'))
                
                response = self.socket.recv(1024).decode('utf-8')
                if response == "AUTH_SUCCESS":
                    Clock.schedule_once(lambda dt: self._connection_success())
                    
                    # Start receiving messages
                    threading.Thread(target=self._receive_messages, daemon=True).start()
                else:
                    Clock.schedule_once(lambda dt: self._connection_failed("Invalid PIN"))
                    
        except Exception as e:
            Clock.schedule_once(lambda dt: self._connection_failed(str(e)))
    
    def _connection_success(self):
        """Handle successful connection"""
        self.root.current = 'chat'
    
    def _connection_failed(self, error):
        """Handle connection failure"""
        screen = self.root.get_screen('pin_entry')
        screen.status_label.text = f'Connection failed: {error}'
    
    def _receive_messages(self):
        """Receive messages from host"""
        try:
            while self.running:
                data = self.socket.recv(1024)
                if not data:
                    break
                
                message = data.decode('utf-8')
                if ': ' in message:
                    sender, content = message.split(': ', 1)
                    self.message_manager.add_message(sender, content)
                    
        except Exception as e:
            print(f"Receive error: {e}")
    
    def send_message(self, message):
        """Send a message"""
        sender = "host" if self.is_host else "me"
        self.message_manager.add_message(sender, message)
        
        if self.is_host:
            # Broadcast to all clients
            for client_socket in self.clients:
                try:
                    client_socket.send(f"host: {message}".encode('utf-8'))
                except:
                    pass
        else:
            # Send to host
            try:
                self.socket.send(message.encode('utf-8'))
            except Exception as e:
                print(f"Send error: {e}")
    
    def get_messages(self):
        """Get all messages"""
        return self.message_manager.get_messages()
    
    def on_stop(self):
        """Cleanup when app stops"""
        self.running = False
        
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
        
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
        
        for client_socket in self.clients:
            try:
                client_socket.close()
            except:
                pass
        
        self.message_manager.stop()


if __name__ == '__main__':
    BluetoothMessengerApp().run()
