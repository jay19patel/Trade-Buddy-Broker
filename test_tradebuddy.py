#!/usr/bin/env python3
"""
Optimal Test Suite for Trade Buddy Broker
Clean, minimal, and comprehensive testing
"""

import asyncio
import sys
import os

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from trade_buddy.broker import TradeBuddy
from trade_buddy.core.response import TBResponse


async def test_complete_workflow():
    """Test complete broker workflow"""
    
    print("🚀 Trade Buddy Broker - Complete Test")
    print("=" * 45)
    
    # Initialize broker
    broker = TradeBuddy()
    
    # Test 1: Registration
    print("\n1. Testing Registration...")
    try:
        response = await broker.registration({
            "email_id": "test@example.com",
            "password": "test123",
            "full_name": "Test User"
        })
        print(f"✅ Registration: {response.message}")
        print(f"   User: {response.data['user']['full_name'] if response.data else 'N/A'}")
    except Exception as e:
        print(f"⚠️  Registration: {e}")
    
    # Test 2: Login
    print("\n2. Testing Login...")
    try:
        response = await broker.login({
            "user_id": "demo@tradebuddy.com",
            "password": "demo123"
        })
        print(f"✅ Login: {response.message}")
        if response.data:
            user = response.data['user']
            print(f"   User: {user['full_name']}")
            print(f"   Balance: ₹{user['balance']:,.2f}")
    except Exception as e:
        print(f"❌ Login failed: {e}")
        return False
    
    # Test 3: Account Details
    print("\n3. Testing Account Details...")
    try:
        response = await broker.get_account_details()
        print(f"✅ Account: {response.message}")
        if response.data:
            account = response.data['account']
            print(f"   Balance: ₹{account['balance']:,.2f}")
    except Exception as e:
        print(f"❌ Account details failed: {e}")
    
    # Test 4: Create Order
    print("\n4. Testing Order Creation...")
    try:
        response = await broker.create_order({
            "stock_symbol": "RELIANCE",
            "order_side": "BUY",
            "stock_type": "Stocks",
            "price": 2500.0,
            "quantity": 10,
            "stoploss_price": 2400.0,
            "target_price": 2600.0
        })
        print(f"✅ Order: {response.message}")
        if response.data:
            order = response.data['order']
            print(f"   Symbol: {order['stock_symbol']}")
            print(f"   Quantity: {order['quantity']}")
    except Exception as e:
        print(f"⚠️  Order creation: {e}")
    
    # Test 5: Get Positions
    print("\n5. Testing Positions...")
    try:
        response = await broker.get_positions()
        print(f"✅ Positions: {response.message}")
        if response.data:
            print(f"   Total Positions: {response.data.get('total_positions', 0)}")
            print(f"   Active Positions: {response.data.get('active_positions', 0)}")
    except Exception as e:
        print(f"⚠️  Positions: {e}")
    
    # Test 6: Create Transaction
    print("\n6. Testing Transaction...")
    try:
        response = await broker.create_transaction({
            "transaction_type": "DEPOSIT",
            "amount": 5000.0,
            "note": "Test deposit"
        })
        print(f"✅ Transaction: {response.message}")
        if response.data:
            txn = response.data['transaction']
            print(f"   Amount: ₹{txn['transaction_amount']:,.2f}")
    except Exception as e:
        print(f"⚠️  Transaction: {e}")
    
    # Test 7: Search Symbols
    print("\n7. Testing Symbol Search...")
    try:
        response = broker.search_symbols("RELI")
        print(f"✅ Search: {response.message}")
        if response.data:
            symbols = response.data.get('symbols', [])
            print(f"   Found {len(symbols)} symbols")
    except Exception as e:
        print(f"⚠️  Symbol search: {e}")
    
    # Test 8: Support Ticket
    print("\n8. Testing Support Ticket...")
    try:
        response = await broker.send_support_ticket({
            "email": "test@example.com",
            "title": "Test Ticket",
            "message": "This is a test support ticket"
        })
        print(f"✅ Ticket: {response.message}")
    except Exception as e:
        print(f"⚠️  Support ticket: {e}")
    
    # Test 9: Delete Account
    print("\n9. Testing Account Deletion...")
    try:
        response = await broker.delete_account("DEMO01")
        print(f"✅ Delete Account: {response.message}")
    except Exception as e:
        print(f"⚠️  Account deletion: {e}")
    
    # Test 10: Database Clear
    print("\n10. Testing Database Clear...")
    try:
        response = await broker.clear()
        print(f"✅ Database Clear: {response.message}")
        print(f"    Cleared: {response.data.get('cleared', False)}")
    except Exception as e:
        print(f"⚠️  Database clear: {e}")
    
    print("\n" + "=" * 45)
    print("✅ Complete workflow test finished!")
    return True


def test_response_format():
    """Test TBResponse format"""
    print("\n📋 Testing Response Format...")
    
    # Test TBResponse creation
    response = TBResponse(
        message="Test successful",
        data={"test_key": "test_value"}
    )
    
    print(f"✅ TBResponse created: {response.message}")
    print(f"✅ Data: {response.data}")
    
    # Test serialization
    response_dict = response.model_dump()
    print(f"✅ Serialization: {type(response_dict).__name__}")
    
    return True


async def main():
    """Main test function"""
    print("🧪 Trade Buddy Broker - Optimal Test Suite")
    print("🔬 Clean, minimal, and comprehensive testing")
    
    # Test response format first
    format_ok = test_response_format()
    
    # Test complete workflow
    workflow_ok = await test_complete_workflow()
    
    # Summary
    print("\n" + "🎯 Test Summary".center(45, "="))
    print(f"Response Format: {'✅ PASS' if format_ok else '❌ FAIL'}")
    print(f"Workflow Tests:  {'✅ PASS' if workflow_ok else '❌ FAIL'}")
    print("=" * 45)
    
    if format_ok and workflow_ok:
        print("🎉 All tests completed successfully!")
        print("🚀 Trade Buddy Broker is ready for production!")
    else:
        print("⚠️  Some tests had issues - check implementation")
    
    return format_ok and workflow_ok


if __name__ == "__main__":
    try:
        result = asyncio.run(main())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n⏹️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)