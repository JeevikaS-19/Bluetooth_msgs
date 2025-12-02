"""
Message manager for in-memory storage with auto-deletion.
Messages are stored in RAM and automatically deleted after 5 minutes.
"""

import threading
import time
from datetime import datetime, timedelta
from collections import deque


class Message:
    """Represents a single message with timestamp."""
    
    def __init__(self, sender, content):
        self.sender = sender
        self.content = content
        self.timestamp = datetime.now()
    
    def __str__(self):
        time_str = self.timestamp.strftime("%H:%M:%S")
        return f"[{time_str}] {self.sender}: {self.content}"
    
    def is_expired(self, expiry_minutes=5):
        """Check if message has expired.
        
        Args:
            expiry_minutes: Number of minutes before expiry (default: 5)
            
        Returns:
            bool: True if expired, False otherwise
        """
        return datetime.now() - self.timestamp > timedelta(minutes=expiry_minutes)


class MessageManager:
    """Manages in-memory message storage with auto-deletion."""
    
    def __init__(self, expiry_minutes=5):
        self.messages = deque()
        self.expiry_minutes = expiry_minutes
        self.lock = threading.Lock()
        self.running = True
        
        # Start cleanup thread
        self.cleanup_thread = threading.Thread(target=self._cleanup_loop, daemon=True)
        self.cleanup_thread.start()
    
    def add_message(self, sender, content):
        """Add a new message to storage.
        
        Args:
            sender: Identifier of the message sender
            content: Message content
        """
        with self.lock:
            msg = Message(sender, content)
            self.messages.append(msg)
    
    def get_messages(self, limit=None):
        """Get all non-expired messages.
        
        Args:
            limit: Maximum number of messages to return (None for all)
            
        Returns:
            list: List of Message objects
        """
        with self.lock:
            if limit:
                return list(self.messages)[-limit:]
            return list(self.messages)
    
    def _cleanup_loop(self):
        """Background thread that removes expired messages."""
        while self.running:
            time.sleep(30)  # Check every 30 seconds
            self._cleanup_expired()
    
    def _cleanup_expired(self):
        """Remove expired messages from storage."""
        with self.lock:
            # Remove expired messages from the front
            while self.messages and self.messages[0].is_expired(self.expiry_minutes):
                self.messages.popleft()
    
    def stop(self):
        """Stop the cleanup thread."""
        self.running = False
