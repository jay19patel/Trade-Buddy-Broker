"""
Security utilities with singleton pattern
"""

import secrets
import string
import time
import uuid
import bcrypt
import jwt
from datetime import timedelta, datetime
from typing import Dict, Any, Optional
from .singleton import Singleton
from ..core.exceptions import TradeBuddyException, AuthenticationError, ValidationError


class SecurityManager(Singleton):
    """Security manager singleton"""
    
    def __init__(self, secret_key: str = "trade-buddy-secret-key-2024", algorithm: str = "HS256"):
        if not hasattr(self, 'initialized'):
            self.secret_key = secret_key
            self.algorithm = algorithm
            self.initialized = True
    
    def generate_unique_id(self, prefix: str) -> str:
        """Generate unique ID with prefix"""
        timestamp = int(time.time() * 1000)  # milliseconds
        unique_string = f"TB-{timestamp}-{prefix.upper()}"
        return unique_string
    
    def generate_unique_account_id(self, existing_ids: set = None) -> str:
        """Generate unique account ID"""
        characters = string.ascii_uppercase + string.digits
        existing_ids = existing_ids or set()
        
        max_attempts = 1000
        attempts = 0
        
        while attempts < max_attempts:
            new_id = ''.join(secrets.choice(characters) for _ in range(6))
            if new_id not in existing_ids:
                return new_id
            attempts += 1
        
        raise TradeBuddyException("Unable to generate unique account ID")
    
    def generate_hash_password(self, password: str) -> str:
        """Generate hashed password"""
        if not password:
            raise ValidationError("Password cannot be empty")
        
        hash_password = password.encode("utf-8")
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(hash_password, salt)
        return hashed_password.decode('utf-8')
    
    def check_hash_password(self, password: str, hashed_password: str) -> bool:
        """Check if password matches hashed password"""
        try:
            if not password or not hashed_password:
                return False
            return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
        except Exception:
            return False
    
    def create_access_token(self, payload: Dict[str, Any], expiry: timedelta = None) -> str:
        """Create JWT access token"""
        if not payload:
            raise TradeBuddyException("Payload cannot be empty")
        
        token_payload = payload.copy()
        if expiry is None:
            expiry = timedelta(hours=24)
        
        token_payload['exp'] = datetime.utcnow() + expiry
        token_payload['iat'] = datetime.utcnow()
        token_payload['jti'] = str(uuid.uuid4())
        
        try:
            token = jwt.encode(token_payload, self.secret_key, algorithm=self.algorithm)
            return token
        except Exception as e:
            raise TradeBuddyException(f"Failed to create access token: {str(e)}")
    
    def decode_token(self, token: str) -> Dict[str, Any]:
        """Decode JWT token"""
        if not token:
            raise AuthenticationError("Token cannot be empty")
        
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            raise AuthenticationError("Access token has expired")
        except jwt.InvalidTokenError:
            raise AuthenticationError("Invalid token")
        except Exception as e:
            raise AuthenticationError(f"Token validation failed: {str(e)}")
    
    def validate_token(self, token: str) -> bool:
        """Validate token without raising exceptions"""
        try:
            self.decode_token(token)
            return True
        except:
            return False