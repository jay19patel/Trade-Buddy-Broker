"""
Authentication service
"""

from datetime import timedelta
from typing import Optional
from trade_buddy.entities.models import Account
from trade_buddy.entities.schemas import RegistrationSchema, LoginSchema
from trade_buddy.core.exceptions import AuthenticationError, ValidationError
from trade_buddy.core.response import TBResponse
from trade_buddy.utils.security import SecurityManager
from trade_buddy.repositories.account_repository import AccountRepository


class AuthService:
    """Authentication service"""
    
    def __init__(self):
        self.account_repo = AccountRepository()
        self.security = SecurityManager()
    
    async def register(self, data: RegistrationSchema) -> TBResponse:
        """Register new user"""
        try:
            # Generate unique account ID
            existing_accounts = await self.account_repo.get_all()
            existing_ids = {acc.account_id for acc in existing_accounts}
            account_id = self.security.generate_unique_account_id(existing_ids)
            
            # Create account
            account = Account(
                account_id=account_id,
                email_id=data.email_id,
                password=self.security.generate_hash_password(data.password),
                full_name=data.full_name,
                max_trad_per_day=data.max_trad_per_day,
                base_stoploss=data.base_stoploss,
                base_target=data.base_target,
                trailing_status=data.trailing_status,
                trailing_stoploss=data.trailing_stoploss,
                trailing_target=data.trailing_target,
                description=data.description
            )
            
            await self.account_repo.create(account)
            
            # Create verification token
            token = self.security.create_access_token(
                payload={
                    "AccountId": account.account_id,
                    "AccountEmail": account.email_id,
                    "AccountRole": account.role
                },
                expiry=timedelta(hours=24)
            )
            
            return TBResponse(
                message="Registration successful",
                data={
                    "user": account.model_dump_safe(),
                    "verification_token": token
                }
            )
            
        except Exception as e:
            if isinstance(e, (AuthenticationError, ValidationError)):
                raise
            raise ValidationError(f"Registration failed: {str(e)}")
    
    async def login(self, data: LoginSchema) -> TBResponse:
        """Login user"""
        try:
            # Find account
            account = await self.account_repo.get_by_user_id(data.user_id)
            
            if not account:
                raise AuthenticationError("Invalid credentials")
            
            # Check password
            if not self.security.check_hash_password(data.password, account.password):
                raise AuthenticationError("Invalid credentials")
            
            # Check email verification
            if not account.email_verified:
                raise AuthenticationError("Email not verified")
            
            # Create access token
            token = self.security.create_access_token(
                payload={
                    "AccountId": account.account_id,
                    "AccountEmail": account.email_id,
                    "AccountRole": account.role
                },
                expiry=timedelta(hours=24)
            )
            
            return TBResponse(
                message="Login successful",
                data={
                    "account_id": account.account_id,
                    "role": account.role,
                    "access_token": token,
                    "full_name": account.full_name
                }
            )
            
        except Exception as e:
            if isinstance(e, AuthenticationError):
                raise
            raise AuthenticationError(f"Login failed: {str(e)}")
    
    async def verify_token(self, token: str) -> Optional[Account]:
        """Verify access token and return account"""
        try:
            payload = self.security.decode_token(token)
            account_id = payload.get("AccountId")
            
            if not account_id:
                raise AuthenticationError("Invalid token payload")
            
            account = await self.account_repo.get_by_id(account_id)
            if not account:
                raise AuthenticationError("Account not found")
            
            return account
            
        except Exception as e:
            if isinstance(e, AuthenticationError):
                raise
            raise AuthenticationError(f"Token verification failed: {str(e)}")
    
    async def verify_email(self, token: str) -> TBResponse:
        """Verify email with token"""
        try:
            payload = self.security.decode_token(token)
            email = payload.get("AccountEmail")
            
            if not email:
                raise ValidationError("Invalid verification token")
            
            account = await self.account_repo.get_by_email(email)
            if not account:
                raise ValidationError("Account not found")
            
            if not account.email_verified:
                account.email_verified = True
                await self.account_repo.update(account)
                
                return TBResponse(
                    message="Email verified successfully",
                    data={"account_id": account.account_id}
                )
            
            return TBResponse(
                message="Email already verified",
                data={"account_id": account.account_id}
            )
            
        except Exception as e:
            if isinstance(e, (AuthenticationError, ValidationError)):
                raise
            raise ValidationError(f"Email verification failed: {str(e)}")