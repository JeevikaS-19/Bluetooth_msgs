"""
Bluetooth Client
Discovers and connects to the host, authenticates, and exchanges messages.
"""

import bluetooth
import threading
import sys
from message_manager import MessageManager


class BluetoothClient:
    """Bluetooth client that connects to the host server."""
    
    def __init__(self):
        self.message_manager = MessageManager(expiry_minutes=5)
        self.socket = None
        self.running = True
        self.connected = False
    
    def discover_and_connect(self):
        """Discover nearby Bluetooth devices and connect to host."""
        print("\n" + "="*50)
        print("BLUETOOTH MESSENGER - CLIENT MODE")
        print("="*50)
        
        print("\nSearching for Bluetooth devices...")
        
        try:
            nearby_devices = bluetooth.discover_devices(
                duration=8,
                lookup_names=True,
                flush_cache=True
            )
            
            if not nearby_devices:
                print("No Bluetooth devices found.")
                print("\nMake sure:")
                print("  1. Bluetooth is enabled on both devices")
                print("  2. The host is running and discoverable")
                print("  3. Devices are paired (if required by your OS)")
                sys.exit(1)
            
            print(f"\nFound {len(nearby_devices)} device(s):")
            for i, (addr, name) in enumerate(nearby_devices):
                print(f"  {i+1}. {name} ({addr})")
            
            # Let user select device
            while True:
                try:
                    choice = input("\nSelect device number (or 'q' to quit): ")
                    if choice.lower() == 'q':
                        sys.exit(0)
                    
                    device_index = int(choice) - 1
                    if 0 <= device_index < len(nearby_devices):
                        selected_device = nearby_devices[device_index]
                        break
                    else:
                        print("Invalid selection. Try again.")
                except ValueError:
                    print("Invalid input. Enter a number.")
            
            host_addr = selected_device[0]
            host_name = selected_device[1]
            
            print(f"\nConnecting to {host_name}...")
            
            # Find the service
            service_matches = bluetooth.find_service(
                name="BluetoothMessenger",
                address=host_addr
            )
            
            if not service_matches:
                print("BluetoothMessenger service not found on this device.")
                sys.exit(1)
            
            first_match = service_matches[0]
            port = first_match["port"]
            
            # Connect
            self.socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
            self.socket.connect((host_addr, port))
            
            print("Connected! Authenticating...")
            
            # Handle authentication
            if self._authenticate():
                self.connected = True
                print("✓ Authentication successful!")
                print("\nYou can now send messages.")
                print("Commands: /quit, /messages")
                print("="*50 + "\n")
                
                # Start receiving messages
                receive_thread = threading.Thread(target=self._receive_messages, daemon=True)
                receive_thread.start()
                
                # Handle user input
                self._handle_input()
            else:
                print("✗ Authentication failed. Incorrect PIN.")
                self.socket.close()
                sys.exit(1)
                
        except Exception as e:
            print(f"\nError: {e}")
            print("\nTroubleshooting:")
            print("  - Ensure Bluetooth is enabled")
            print("  - Make sure devices are paired")
            print("  - Check that the host is running")
            sys.exit(1)
    
    def _authenticate(self):
        """Authenticate with the host.
        
        Returns:
            bool: True if authentication successful, False otherwise
        """
        try:
            # Wait for auth request
            data = self.socket.recv(1024).decode('utf-8')
            
            if data == "AUTH_REQUEST":
                # Get PIN from user
                pin = input("Enter authentication PIN: ")
                
                # Send PIN
                self.socket.send(pin.encode('utf-8'))
                
                # Wait for response
                response = self.socket.recv(1024).decode('utf-8')
                
                return response == "AUTH_SUCCESS"
            
            return False
            
        except Exception as e:
            print(f"Authentication error: {e}")
            return False
    
    def _receive_messages(self):
        """Receive messages from the host and other peers."""
        try:
            while self.running and self.connected:
                data = self.socket.recv(1024)
                if not data:
                    break
                
                message = data.decode('utf-8')
                
                # Parse sender and content
                if ': ' in message:
                    sender, content = message.split(': ', 1)
                    self.message_manager.add_message(sender, content)
                    
                    # Display the message
                    messages = self.message_manager.get_messages(limit=1)
                    if messages:
                        print(f"\n{messages[-1]}")
                        print("\nme> ", end='', flush=True)
                
        except Exception as e:
            if self.running:
                print(f"\n\nConnection lost: {e}")
        finally:
            self.connected = False
            print("\n\nDisconnected from host.")
            self.stop()
    
    def _handle_input(self):
        """Handle user input for sending messages."""
        try:
            while self.running and self.connected:
                message = input("\nme> ")
                
                if message.lower() == '/quit':
                    print("\nDisconnecting...")
                    self.stop()
                    break
                elif message.lower() == '/messages':
                    print("\n--- Recent Messages ---")
                    messages = self.message_manager.get_messages()
                    if messages:
                        for msg in messages:
                            print(msg)
                    else:
                        print("  (no messages)")
                    print("-----------------------")
                elif message.strip():
                    # Send message to host
                    try:
                        self.socket.send(message.encode('utf-8'))
                        self.message_manager.add_message("me", message)
                    except Exception as e:
                        print(f"\nError sending message: {e}")
                        self.connected = False
                        break
                        
        except KeyboardInterrupt:
            print("\n\nDisconnecting...")
            self.stop()
    
    def stop(self):
        """Stop the client and cleanup."""
        self.running = False
        self.connected = False
        
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
        
        self.message_manager.stop()
        print("Client stopped.")
        sys.exit(0)


if __name__ == "__main__":
    client = BluetoothClient()
    client.discover_and_connect()
