"""
Singleton pattern implementation
"""

import threading
from typing import Dict, Any


class SingletonMeta(type):
    """Singleton metaclass"""
    _instances: Dict[type, Any] = {}
    _lock: threading.Lock = threading.Lock()

    def __call__(cls, *args, **kwargs):
        """Thread-safe singleton implementation"""
        if cls not in cls._instances:
            with cls._lock:
                # Double-checked locking pattern
                if cls not in cls._instances:
                    cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class Singleton(metaclass=SingletonMeta):
    """Base singleton class"""
    pass