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

    print("\n== Email Verification ==")
    try:
        # Get verification token from registration response
        verification_token = reg.data["verification_token"]
        verify_response = await broker.verify_email(verification_token)
        print("Email verification:", verify_response.message)
    except Exception as e:
        print("Email verification error:", e)

    print("\n== Login ==")
    try:
        login = await broker.login({"user_id": "demo_test@example.com", "password": "password123"})
        if not login.data:
            print("Login failed:", login.message)
            return
        print("Login:", login.message)
        # Extract account object for all subsequent calls
        account = login.data.get("account")
    except Exception as e:
        print("Login error:", e)
        return

    print("\n== Account Details ==")
    # Already have account from login; fall back to broker helper if missing
    if not account:
        account = await broker.get_account()
    
    # If account is a dict, we need to convert it to Account model
    if isinstance(account, dict):
        from trade_buddy.entities.models import Account
        account = Account(**account)
    
    acc = await broker.get_account_details(account)
    print(acc.message, acc.data)

    print("\n== Create Deposit Transaction ==")
    dep = await broker.create_transaction(account, {"transaction_type": "DEPOSIT", "amount": 1000.0, "note": "Init deposit"})
    print(dep.message, dep.data)

    print("\n== Create Withdraw Transaction ==")
    wd = await broker.create_transaction(account, {"transaction_type": "WITHDRAW", "amount": 200.0, "note": "Test withdraw"})
    print(wd.message, wd.data)

    print("\n== Prices ==")
    print(broker.get_live_price("RELIANCE", "Stocks").message)
    print(broker.get_multiple_prices([
        {"symbol_id": "RELIANCE", "symbol_type": "Stocks"},
        {"symbol_id": "HDFC", "symbol_type": "Stocks"}
    ]).message)

    print("\n== Positions ==")
    op = await broker.open_position(account, "RELIANCE", quantity=10, price=2500.0, side="BUY", stoploss=2450.0, target=2600.0)
    pos_id = op.data["position"]["position_id"]
    print(op.message, op.data)

    upd = await broker.update_position_levels(account, pos_id, stoploss=2460.0, target=2590.0)
    print(upd.message, upd.data)

    # Test pyramiding (add to position)
    print("\n== Pyramiding ==")
    pyr = await broker.pyramid(account, pos_id, additional_quantity=5, new_price=2510.0)
    print(pyr.message, pyr.data)

    # Test trailing (partial close + optional SL/TP update)
    print("\n== Trailing (Partial Close) ==")
    trl = await broker.trailing(account, pos_id, close_quantity=3, exit_price=2525.0, stoploss=2470.0, target=2580.0)
    print(trl.message, trl.data)

    open_list = await broker.get_open_positions(account)
    print(open_list.message, open_list.data)

    exited = await broker.exit_position(account, pos_id, exit_price=2550.0)
    print(exited.message, exited.data)

    hist = await broker.get_position_history(account)
    print(hist.message, hist.data)

    # Test leverage update and effect on new position
    print("\n== Update Leverage ==")
    lev = await broker.update_leverage(account, 2.0)
    print(lev.message, lev.data)

    print("\n== Open Position With New Leverage ==")
    op2 = await broker.open_position(account, "HDFC", quantity=4, price=1600.0, side="BUY")
    print(op2.message, op2.data)

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

    # Test notifications
    print("\n== Notifications ==")
    notifications = await broker.get_notifications(account, limit=10)
    print("All notifications:", notifications.message, len(notifications.data.get("notifications", [])))
    
    # Test notifications by type
    transaction_notifications = await broker.get_notifications_by_type(account, "TRANSACTION", limit=5)
    print("Transaction notifications:", transaction_notifications.message, len(transaction_notifications.data.get("notifications", [])))
    
    position_notifications = await broker.get_notifications_by_type(account, "POSITION", limit=5)
    print("Position notifications:", position_notifications.message, len(position_notifications.data.get("notifications", [])))
    
    # Test notification subscriptions
    print("\n== Notification Subscriptions ==")
    # Defaults: database + push enabled
    # Enable email channel (prints only)
    broker.notification_subscribe(["email"])  # enable email
    # Optionally set email config (dummy)
    broker.notification_set_email({
        "smtp_host": "smtp.example.com",
        "smtp_port": 587,
        "from_email": "noreply@example.com",
        "to_email": "demo_test@example.com"
    })
    print("Notification channels updated: +email")
    
    # Test error notification by trying invalid operation
    print("\n== Test Error Notification ==")
    try:
        await broker.open_position(account, "INVALID", quantity=-1, price=100.0, side="BUY")
    except Exception as e:
        print(f"Expected error caught: {e}")
    
    # Check error notifications
    error_notifications = await broker.get_notifications_by_type(account, "ERROR", limit=5)
    print("Error notifications:", error_notifications.message, len(error_notifications.data.get("notifications", [])))
    
    print("\n== Logout ==")
    lo = await broker.logout()
    print(lo.message, lo.data)


if __name__ == "__main__":
    asyncio.run(run())


