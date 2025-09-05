#!/usr/bin/env python3
import asyncio
from trade_buddy.broker import TradeBuddy


async def run():
    # Recreate DB schema to include latest columns (positions, leverage, etc.)
    from trade_buddy.core.database import get_database_manager
    db = get_database_manager()
    try:
        await db.drop_tables()
    except Exception:
        pass
    await db.create_tables()

    broker = TradeBuddy()

    print("== Registration ==")
    try:
        reg = await broker.registration({
            "email_id": "demo_test@example.com",
            "password": "password123",
            "full_name": "Demo Tester",
            "max_trad_per_day": 10,
            "base_stoploss": 5.0,
            "base_target": 10.0,
            "trailing_status": True,
            "trailing_stoploss": 8.0,
            "trailing_target": 15.0,
            "description": "SDK E2E"
        })
        print("Registration:", reg.message)
    except Exception as e:
        print("Registration error:", e)

    print("\n== Login ==")
    try:
        login = await broker.login({"user_id": "demo@tradebuddy.com", "password": "demo123"})
        if not login.data:
            print("Login failed:", login.message)
            return
        print("Login:", login.message)
    except Exception as e:
        print("Login error:", e)
        return

    print("\n== Account Details ==")
    acc = await broker.get_account_details()
    print(acc.message, acc.data)

    print("\n== Create Deposit Transaction ==")
    dep = await broker.create_transaction({"transaction_type": "DEPOSIT", "amount": 1000.0, "note": "Init deposit"})
    print(dep.message, dep.data)

    print("\n== Create Withdraw Transaction ==")
    wd = await broker.create_transaction({"transaction_type": "WITHDRAW", "amount": 200.0, "note": "Test withdraw"})
    print(wd.message, wd.data)

    print("\n== Prices ==")
    print(broker.get_live_price("RELIANCE", "Stocks").message)
    print(broker.get_multiple_prices([
        {"symbol_id": "RELIANCE", "symbol_type": "Stocks"},
        {"symbol_id": "HDFC", "symbol_type": "Stocks"}
    ]).message)

    print("\n== Positions ==")
    op = await broker.open_position("RELIANCE", quantity=10, price=2500.0, side="BUY", stoploss=2450.0, target=2600.0)
    pos_id = op.data["position"]["position_id"]
    print(op.message, op.data)

    upd = await broker.update_position_levels(pos_id, stoploss=2460.0, target=2590.0)
    print(upd.message, upd.data)

    open_list = await broker.get_open_positions()
    print(open_list.message, open_list.data)

    exited = await broker.exit_position(pos_id, exit_price=2550.0)
    print(exited.message, exited.data)

    hist = await broker.get_position_history()
    print(hist.message, hist.data)

    print("\n== Session Info ==")
    print(await broker.get_session_info())

    print("\n== Validate Token ==")
    sess = await broker.get_session_info()
    if sess and "jwt_token" in sess:
        vt = await broker.validate_token(sess["jwt_token"])
        print(vt.message, vt.data)

    print("\n== Cleanup Expired Sessions ==")
    from trade_buddy.core.database import get_database_manager
    db = get_database_manager()
    await db.cleanup_expired_sessions()
    print("Cleanup executed")

    print("\n== Logout ==")
    lo = await broker.logout()
    print(lo.message, lo.data)


if __name__ == "__main__":
    asyncio.run(run())


