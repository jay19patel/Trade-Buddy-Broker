from fastapi import status, APIRouter, Depends, Response,Request,BackgroundTasks
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select, or_
from datetime import timedelta,datetime
import logging
from fastapi.templating import Jinja2Templates
import asyncio
# APP
from app.Database.base import AsyncSession, get_db
from app.Schemas.auth_schema import Registration, Login
from app.Models.model import Account
from app.Core.responseBytb import TBException, TBResponse
from app.Core.security import generate_hash_password, check_hash_password, create_access_token, generate_unique_account_id,decode_token,get_account_from_token
from app.Core.config import setting
from app.Services.email import email_send_access_token
auth_rout = APIRouter()
templates = Jinja2Templates(directory="app/html_templates")


@auth_rout.post("/registration")
async def registration(request: Registration, background_tasks: BackgroundTasks, db: AsyncSession = Depends(get_db)) -> TBResponse:
    try:
        account = Account(
            email_id=request.email_id,
            account_id=await generate_unique_account_id(),
            password=generate_hash_password(password=request.password),
            full_name=request.full_name,
            max_trad_per_day=request.max_trad_per_day,
            base_stoploss=request.base_stoploss,
            base_target=request.base_target,
            trailing_status=request.trailing_status,
            trailing_stoploss=request.trailing_stoploss,
            trailing_target=request.trailing_target,
            description=request.description
        )
        db.add(account)
        await db.commit()
        await db.refresh(account)
        access_token = create_access_token(payload={
                                                        "AccountId": account.account_id,
                                                        "AccountEmail": account.email_id,
                                                        "AccountRole": account.role
                                                        }, expiry=timedelta(hours=setting.ACCESS_TOKEN_EXPIRY))
        loop = asyncio.get_event_loop()                  
        background_tasks.add_task(lambda: loop.create_task(email_send_access_token([account.email_id],access_token)))
        return TBResponse(
            message="Registration Successful",
            payload={
                "account_id": account.account_id,
                "email_id": account.email_id,
                "full_name": account.full_name
            }
        )
        
    
    except IntegrityError:
        await db.rollback()
        raise TBException(
            message="The provided email address is already registered.",
            resolution="Please use a different email address or reset your password.",
            status_code=status.HTTP_400_BAD_REQUEST
        )

    except Exception as e:
        await db.rollback()
        raise TBException(
            message="An unexpected error occurred during registration.",
            resolution=str(e),
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@auth_rout.post("/login")
async def login_account(response: Response,
                        request: Login, 
                        db: AsyncSession = Depends(get_db)) -> TBResponse:
    try:
        result = await db.execute(select(Account).where(
            or_(Account.email_id == request.user_id, Account.account_id == request.user_id)
        ))
        account = result.scalars().first()
        if not account:
            raise TBException(message="User not found",
                              resolution="Try with another email id or Account id",
                              status_code=status.HTTP_404_NOT_FOUND)
        
        if not check_hash_password(password=request.password, hashed_password=account.password):
            raise TBException(message="Invalid password",
                              resolution="Try Again",
                              status_code=status.HTTP_403_FORBIDDEN)
        
        if not account.email_verified:
            raise TBException(message="Email not verified. Check your email.",
                              resolution="Check our email and verify your email.",
                              status_code=status.HTTP_403_FORBIDDEN)

        access_token = create_access_token(payload={
            "AccountId": account.account_id,
            "AccountEmail": account.email_id,
            "AccountRole": account.role
        }, expiry=timedelta(seconds=setting.ACCESS_TOKEN_EXPIRY))
        
        return TBResponse(
            message="Login successful",
            payload={
                "account": account.account_id,
                "role": account.role,
                "access_token": access_token,
                "full_name": account.full_name,
            }
        )
    except TBException as tb_exc:
        raise tb_exc  # Re-raise known exceptions for proper handling
    except Exception as e:
        raise TBException(
            message="An unexpected error occurred during login.",
            resolution=str(e),
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@auth_rout.get("/account", status_code=status.HTTP_201_CREATED)
async def account_detail(account:Account = Depends(get_account_from_token), db: AsyncSession = Depends(get_db)):
    return {
        "msg": "Welcome Account User",
        "account": account
    }



@auth_rout.get("/verify_email/verification/{AccessToken}", status_code=status.HTTP_200_OK)
async def verify_email_verification(AccessToken,
                                    request: Request,
                                    db: AsyncSession = Depends(get_db)):
    token_data = decode_token(AccessToken)
    if not token_data:
        return templates.TemplateResponse("verify_faild.html", {"request": request})
    result = await db.execute(select(Account).where(Account.email_id == token_data["AccountEmail"]))
    account = result.scalars().first()
    if not account.email_verified:
        account.email_verified = True
        await db.commit()   
        return templates.TemplateResponse("verify_success.html", {"request": request,"user":account})
    return templates.TemplateResponse("verify_success.html", {"request": request,"user":account})


@auth_rout.get("/verify_email/send_token/{email}", status_code=status.HTTP_200_OK)
async def verify_email_send_token(email,
                                  background_tasks : BackgroundTasks,
                                  db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(Account).where(Account.email_id == email))
        account = result.scalars().first()
        if not account:
            raise TBException(message="email id is not valid",
                              resolution="Try Again.",
                              status_code= status.HTTP_404_NOT_FOUND)
        if not account.email_verified:
            access_token = create_access_token(payload={
                                                        "AccountId": account.account_id,
                                                        "AccountEmail": account.email_id,
                                                        "AccountRole": account.role
                                                        }, expiry=timedelta(hours=setting.ACCESS_TOKEN_EXPIRY)) 
            loop = asyncio.get_event_loop()                  
            background_tasks.add_task(lambda: loop.create_task(email_send_access_token([account.email_id],access_token)))
            return TBResponse(
                message= "Email sent successfully",
                payload= {"access_token": str(access_token),
                            "link_for_verification":f"http://localhost:8080/auth/verify_email/verification/{access_token}"                            
                            })
        return {"message": "Email Alredy Verified"}
    except Exception as e:
        raise TBException(
            message="An error occurred during creating order.",
            resolution=str(e),
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

