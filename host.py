"""
Bluetooth Host Server
Accepts connections from multiple clients, manages authentication, and broadcasts messages.
"""

import bluetooth
import threading
import sys
from auth import AuthManager
from message_manager import MessageManager


class BluetoothHost:
    """Bluetooth server that manages multiple client connections."""
    
    def __init__(self):
        self.auth = AuthManager()
        self.message_manager = MessageManager(expiry_minutes=5)
        self.clients = {}  # {socket: peer_name}
        self.client_counter = 0
        self.lock = threading.Lock()
        self.server_socket = None
        self.running = True
    
    def start(self):
        """Start the Bluetooth host server."""
        # Generate authentication PIN
        pin = self.auth.generate_pin()
        print("\n" + "="*50)
        print("BLUETOOTH MESSENGER - HOST MODE")
        print("="*50)
        print(f"\nAuthentication PIN: {pin}")
        print("Share this PIN with clients to allow connections.")
        print("\nWaiting for connections...")
        print("="*50 + "\n")
        
        # Create Bluetooth server socket
        try:
            self.server_socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
            self.server_socket.bind(("", bluetooth.PORT_ANY))
            self.server_socket.listen(5)
            
            port = self.server_socket.getsockname()[1]
            
            # Advertise service
            bluetooth.advertise_service(
                self.server_socket,
                "BluetoothMessenger",
                service_id="00001101-0000-1000-8000-00805F9B34FB",
                service_classes=["00001101-0000-1000-8000-00805F9B34FB"],
                profiles=[("00001101-0000-1000-8000-00805F9B34FB", 0x0100)]
            )
            
            # Start accepting connections in a separate thread
            accept_thread = threading.Thread(target=self._accept_connections, daemon=True)
            accept_thread.start()
            
            # Start input handling
            self._handle_input()
            
        except Exception as e:
            print(f"Error starting server: {e}")
            print("\nMake sure Bluetooth is enabled and you have necessary permissions.")
            sys.exit(1)
    
    def _accept_connections(self):
        """Accept incoming client connections."""
        while self.running:
            try:
                client_socket, client_info = self.server_socket.accept()
                print(f"\nIncoming connection from {client_info}...")
                
                # Handle authentication in a separate thread
                auth_thread = threading.Thread(
                    target=self._authenticate_client,
                    args=(client_socket, client_info),
                    daemon=True
                )
                auth_thread.start()
                
            except Exception as e:
                if self.running:
                    print(f"Error accepting connection: {e}")
    
    def _authenticate_client(self, client_socket, client_info):
        """Authenticate a client connection.
        
        Args:
            client_socket: Client's socket
            client_info: Client's Bluetooth address
        """
        try:
            # Request PIN
            client_socket.send("AUTH_REQUEST".encode('utf-8'))
            
            # Receive PIN
            received_pin = client_socket.recv(1024).decode('utf-8')
            
            if self.auth.validate_pin(received_pin):
                client_socket.send("AUTH_SUCCESS".encode('utf-8'))
                
                with self.lock:
                    self.client_counter += 1
                    peer_name = f"peer{self.client_counter}"
                    self.clients[client_socket] = peer_name
                
                print(f"✓ {peer_name} connected ({client_info})")
                self._display_status()
                
                # Handle client messages
                self._handle_client(client_socket, peer_name)
            else:
                client_socket.send("AUTH_FAILED".encode('utf-8'))
                client_socket.close()
                print(f"✗ Authentication failed for {client_info}")
                
        except Exception as e:
            print(f"Authentication error: {e}")
            try:
                client_socket.close()
            except:
                pass
    
    def _handle_client(self, client_socket, peer_name):
        """Handle messages from a connected client.
        
        Args:
            client_socket: Client's socket
            peer_name: Name assigned to the peer
        """
        try:
            while self.running:
                data = client_socket.recv(1024)
                if not data:
                    break
                
                message = data.decode('utf-8')
                self.message_manager.add_message(peer_name, message)
                
                # Display the message
                messages = self.message_manager.get_messages(limit=1)
                if messages:
                    print(f"\n{messages[-1]}")
                    print("\nhost> ", end='', flush=True)
                
                # Broadcast to other clients
                self._broadcast_message(peer_name, message, exclude=client_socket)
                
        except Exception as e:
            print(f"\nError with {peer_name}: {e}")
        finally:
            self._disconnect_client(client_socket, peer_name)
    
    def _broadcast_message(self, sender, message, exclude=None):
        """Broadcast a message to all connected clients.
        
        Args:
            sender: Name of the message sender
            message: Message content
            exclude: Socket to exclude from broadcast (optional)
        """
        formatted_msg = f"{sender}: {message}"
        
        with self.lock:
            for client_socket in list(self.clients.keys()):
                if client_socket != exclude:
                    try:
                        client_socket.send(formatted_msg.encode('utf-8'))
                    except:
                        # Client disconnected
                        pass
    
    def _disconnect_client(self, client_socket, peer_name):
        """Disconnect a client.
        
        Args:
            client_socket: Client's socket
            peer_name: Name of the peer
        """
        with self.lock:
            if client_socket in self.clients:
                del self.clients[client_socket]
        
        try:
            client_socket.close()
        except:
            pass
        
        print(f"\n✗ {peer_name} disconnected")
        self._display_status()
        print("\nhost> ", end='', flush=True)
    
    def _display_status(self):
        """Display current connection status."""
        with self.lock:
            print("\n--- Connected Peers ---")
            if self.clients:
                for peer_name in self.clients.values():
                    print(f"  • {peer_name}")
            else:
                print("  (none)")
            print("-----------------------")
    
    def _handle_input(self):
        """Handle user input for sending messages."""
        try:
            while self.running:
                message = input("\nhost> ")
                
                if message.lower() == '/quit':
                    print("\nShutting down...")
                    self.stop()
                    break
                elif message.lower() == '/status':
                    self._display_status()
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
                    # Send message to all clients
                    self.message_manager.add_message("host", message)
                    self._broadcast_message("host", message)
                    
        except KeyboardInterrupt:
            print("\n\nShutting down...")
            self.stop()
    
    def stop(self):
        """Stop the server and cleanup."""
        self.running = False
        
        # Close all client connections
        with self.lock:
            for client_socket in list(self.clients.keys()):
                try:
                    client_socket.close()
                except:
                    pass
            self.clients.clear()
        
        # Close server socket
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
        
        # Stop message manager
        self.message_manager.stop()
        
        print("Server stopped.")
        sys.exit(0)


if __name__ == "__main__":
    host = BluetoothHost()
    host.start()
