"""
Trade Buddy SDK - Production Example
"""

import asyncio
from trade_buddy import TradeBuddy


async def main():
    """Complete example of Trade Buddy SDK usage"""
    
    print("🚀 Trade Buddy SDK - Production Example")
    print("=" * 50)
    
    # Initialize broker
    broker = TradeBuddy()
    
    # Wait for initialization
    await asyncio.sleep(0.5)
    
    try:
        print("\n1️⃣ Registration Example")
        print("-" * 30)
        
        registration_data = {
            "email_id": "newuser@example.com",
            "password": "secure123",
            "full_name": "New User",
            "max_trad_per_day": 10,
            "base_stoploss": 5.0,
            "base_target": 10.0,
            "description": "Test user"
        }
        
        try:
            reg_response = await broker.registration(registration_data)
            print(f"✅ {reg_response.message}")
        except Exception as e:
            print(f"ℹ️ Registration: {str(e)}")
        
        print("\n2️⃣ Login with Demo Account")
        print("-" * 30)
        
        login_data = {
            "user_id": "demo@tradebuddy.com", 
            "password": "demo123"
        }
        
        login_response = await broker.login(login_data)
        print(f"✅ {login_response.message}")
        print(f"Account: {login_response.payload['account_id']}")
        
        print("\n3️⃣ Account Details")
        print("-" * 30)
        
        account = await broker.get_account_details()
        print(f"Name: {account['full_name']}")
        print(f"Balance: ₹{account['balance']:,.2f}")
        print(f"Email Verified: {account['email_verified']}")
        
        print("\n4️⃣ Fund Deposit")
        print("-" * 30)
        
        deposit_data = {
            "transaction_type": "DEPOSIT",
            "amount": 25000.0,
            "note": "Initial funding"
        }
        
        deposit_response = await broker.create_transaction(deposit_data)
        print(f"✅ {deposit_response.message}")
        print(f"New Balance: ₹{deposit_response.payload['new_balance']:,.2f}")
        
        print("\n5️⃣ Symbol Search")
        print("-" * 30)
        
        try:
            results = broker.search_symbols("RELIANCE")
            print(f"Found {len(results)} symbols")
        except Exception as e:
            print(f"⚠️ Search: {str(e)}")
        
        print("\n6️⃣ Live Price Data")
        print("-" * 30)
        
        try:
            price = broker.get_live_price("RELIANCE", "Stocks")
            if price:
                print(f"RELIANCE: ₹{price.get('ltp', 'N/A')}")
        except Exception as e:
            print(f"⚠️ Price: {str(e)}")
        
        print("\n7️⃣ Create Order")
        print("-" * 30)
        
        order_data = {
            "stock_symbol": "RELIANCE",
            "order_side": "BUY", 
            "stock_type": "STOCK",
            "price": 2500.0,
            "stoploss_price": 2400.0,
            "target_price": 2600.0,
            "quantity": 10,
            "created_by": "MANUAL"
        }
        
        order_response = await broker.create_order(order_data)
        print(f"✅ {order_response.message}")
        
        print("\n8️⃣ Get Positions")
        print("-" * 30)
        
        positions = await broker.get_positions()
        overview = positions['overview']
        
        print(f"Open Positions: {overview['open_positions']}")
        print(f"Balance: ₹{overview['balance']:,.2f}")
        print(f"P&L: ₹{overview['pnl_total']:,.2f}")
        
        print("\n✅ All operations completed successfully!")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    finally:
        await broker.logout()
        print("\n👋 Session ended")


if __name__ == "__main__":
    asyncio.run(main())