#!/usr/bin/env python3
"""
Test script for the new TradeBuddy broker implementation
"""

import asyncio
import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from trade_buddy.broker import TradeBuddy
from trade_buddy.entities.response_schemas import TBResponse


async def test_broker_implementation():
    """Test the broker implementation"""
    
    print("🚀 Starting Trade Buddy Broker Test")
    print("=" * 50)
    
    # Initialize broker
    broker = TradeBuddy()
    
    # Test registration
    print("\n📝 Testing Registration...")
    registration_data = {
        "email_id": "test@example.com",
        "password": "test123",
        "full_name": "Test User"
    }
    
    try:
        response = await broker.registration(registration_data)
        print(f"✅ Registration Response: {response.message}")
        print(f"📊 Data type: {type(response.data)}")
        if response.data:
            print(f"👤 User: {response.data.get('user', {}).get('full_name', 'N/A')}")
    except Exception as e:
        print(f"❌ Registration failed: {e}")
    
    # Test login
    print("\n🔐 Testing Login...")
    login_data = {
        "user_id": "demo@tradebuddy.com",
        "password": "demo123"
    }
    
    try:
        response = await broker.login(login_data)
        print(f"✅ Login Response: {response.message}")
        if response.data:
            print(f"🔑 Access Token: {response.data.get('access_token', 'N/A')[:20]}...")
            print(f"👤 User: {response.data.get('user', {}).get('full_name', 'N/A')}")
    except Exception as e:
        print(f"❌ Login failed: {e}")
    
    # Test get account details
    print("\n👤 Testing Account Details...")
    try:
        response = await broker.get_account_details()
        print(f"✅ Account Details Response: {response.message}")
        if response.data:
            print(f"💰 Balance: ${response.data.get('account', {}).get('balance', 0)}")
    except Exception as e:
        print(f"❌ Account details failed: {e}")
    
    # Test positions
    print("\n📈 Testing Positions...")
    try:
        response = await broker.get_positions()
        print(f"✅ Positions Response: {response.message}")
        if response.data:
            print(f"📊 Total Positions: {response.data.get('total_positions', 0)}")
    except Exception as e:
        print(f"❌ Positions failed: {e}")
    
    # Test clear method
    print("\n🗑️  Testing Clear Database...")
    try:
        response = await broker.clear()
        print(f"✅ Clear Response: {response.message}")
        print(f"🧹 Cleared: {response.data.get('cleared', False)}")
    except Exception as e:
        print(f"❌ Clear failed: {e}")
    
    print("\n" + "=" * 50)
    print("✅ Trade Buddy Broker Test Complete!")


def test_response_schemas():
    """Test response schemas"""
    print("\n📋 Testing Response Schemas...")
    
    # Test TBResponse
    response = TBResponse(
        message="Test message",
        data={"test": "data"}
    )
    
    print(f"✅ TBResponse created: {response.message}")
    print(f"📊 Data: {response.data}")
    
    # Test serialization
    response_dict = response.model_dump()
    print(f"✅ Serialization works: {type(response_dict)}")


if __name__ == "__main__":
    print("🔬 Testing Response Schemas...")
    test_response_schemas()
    
    print("\n🔬 Testing Async Broker...")
    try:
        asyncio.run(test_broker_implementation())
    except KeyboardInterrupt:
        print("\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()