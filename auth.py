"""
Simple authentication module for Bluetooth messenger.
Generates and validates PINs for secure connections.
"""

import random
import string


class AuthManager:
    """Manages authentication for Bluetooth connections."""
    
    def __init__(self):
        self.pin = None
    
    def generate_pin(self, length=6):
        """Generate a random PIN for authentication.
        
        Args:
            length: Length of the PIN (default: 6)
            
        Returns:
            str: Generated PIN
        """
        self.pin = ''.join(random.choices(string.digits, k=length))
        return self.pin
    
    def validate_pin(self, provided_pin):
        """Validate a provided PIN against the stored PIN.
        
        Args:
            provided_pin: The PIN to validate
            
        Returns:
            bool: True if PIN matches, False otherwise
        """
        return self.pin is not None and provided_pin == self.pin
