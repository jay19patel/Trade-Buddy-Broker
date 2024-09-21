

from fastapi import FastAPI 
from app.Database.base import init_db
from contextlib import asynccontextmanager
from app.Routes.auth import auth_rout
from app.Routes.home import home_route
from app.Routes.transaction import transaction_route
from app.Routes.order import order_route
from app.Routes.analytic import analytics_route
from fastapi.middleware.cors import CORSMiddleware
# Harek Load par aa function execute thase(like.restart par)
from art import text2art
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

scheduler = AsyncIOScheduler()
from app.Core.stop_order_manager import main_auto_stoporder_exit_system



async def scheduled_task():
    now = datetime.now()
    start_time = now.replace(hour=9, minute=15, second=0, microsecond=0)
    end_time = now.replace(hour=15, minute=30, second=0, microsecond=0)

    if start_time <= now <= end_time:
        print(f"Scheduled task started at {now}")
        await main_auto_stoporder_exit_system()



async def start_system():
    print(text2art("TRADE BUDDY",font="small"))
    await init_db()
    # scheduler.add_job(scheduled_task, IntervalTrigger(minutes=1))
    scheduler.start()

async def shutdown_system():
    print(text2art("TRADE BUDDY",font="small"))



@asynccontextmanager
async def connectingTodb(app: FastAPI):
    # await start_system()
    yield
    # await shutdown_system()


app = FastAPI(title="Trade Buddy Order/Position Management System",lifespan=connectingTodb)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(home_route,prefix="/home",tags=["Home"])
app.include_router(auth_rout,prefix="/auth",tags=["Authetication"])
app.include_router(transaction_route,prefix="/transaction",tags=["Transaction"])
app.include_router(order_route,prefix="/order",tags=["Orders"])
app.include_router(analytics_route,prefix="/analytic",tags=["Analytics"])
