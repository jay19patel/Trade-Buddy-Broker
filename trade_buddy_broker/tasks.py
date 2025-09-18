"""
Celery tasks for background processing of long-running operations.

Local-only default:
- Uses in-memory broker/backend and eager execution (runs inline, no external services).
- No Redis required. If you set CELERY_BROKER_URL/RESULT_BACKEND, those will be used.
"""

import os
import asyncio
from celery import Celery


def _make_celery() -> Celery:
    # Default to fully local execution with in-memory broker/backend
    broker_url = os.getenv("CELERY_BROKER_URL", "memory://")
    backend_url = os.getenv("CELERY_RESULT_BACKEND", "cache+memory://")
    app = Celery("trade_buddy", broker=broker_url, backend=backend_url)
    # Run tasks eagerly by default (execute inline, same process)
    app.conf.task_always_eager = True
    app.conf.task_eager_propagates = True
    return app


app = _make_celery()


@app.task(name="trade_buddy.clear_database")
def clear_database_task() -> bool:
    from trade_buddy_broker.core.database import get_database_manager
    from trade_buddy_broker.core.session_manager import DatabaseSessionManager

    async def run():
        db = get_database_manager()
        await db.truncate_all_tables()
        await DatabaseSessionManager().clear_all_sessions()
        return True

    return asyncio.run(run())


@app.task(name="trade_buddy.delete_account")
def delete_account_task(account_id: str) -> bool:
    from trade_buddy_broker.core.database import get_database_manager

    async def run():
        db = get_database_manager()
        await db.clear_account_data(account_id)
        return True

    return asyncio.run(run())


@app.task(name="trade_buddy.cleanup_expired_sessions")
def cleanup_expired_sessions_task() -> int:
    from trade_buddy_broker.core.database import get_database_manager

    async def run():
        db = get_database_manager()
        await db.cleanup_expired_sessions()
        return 1

    return asyncio.run(run())


