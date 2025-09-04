#!/usr/bin/env python3
"""
Broker Test - Mixed Sync/Async Approach for Fast Execution
Fast object creation + Async methods for database operations
"""

import sys
import os
import asyncio
import time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_basic_functionality():
    """Test basic broker functionality - SYNC for speed"""
    print("🚀 Testing Trade Buddy Broker - Mixed Sync/Async")
    print("=" * 55)
    
    try:
        # Import broker (timed)
        start_time = time.time()
        print("1. Importing TradeBuddy...")
        from trade_buddy.broker import TradeBuddy
        import_time = time.time() - start_time
        print(f"   ✅ Import successful! ({import_time:.3f}s)")
        
        # Create broker object (timed - should be fast)
        start_time = time.time()
        print("\n2. Creating TradeBuddy object...")
        broker = TradeBuddy()
        creation_time = time.time() - start_time
        print(f"   ✅ Object created successfully! ({creation_time:.3f}s)")
        
        # Test the test variable (instant)
        print(f"\n3. Testing .test variable...")
        print(f"   ✅ broker.test = '{broker.test}'")
        
        # Test basic properties (instant)
        print(f"\n4. Testing basic properties...")
        print(f"   ✅ Session ID: {broker._current_session_id}")
        print(f"   ✅ Initialized: {broker._initialized}")
        print(f"   ✅ DB Initialized: {broker._db_initialized}")
        
        # Speed analysis
        if creation_time < 0.01:
            print(f"   🚀 EXCELLENT: Object creation is lightning fast!")
        elif creation_time < 0.1:
            print(f"   ✅ GOOD: Object creation is very fast")
        else:
            print(f"   ⚠️  SLOW: Object creation took {creation_time:.3f}s")
        
        return broker
        
    except Exception as e:
        print(f"❌ Basic functionality test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

async def test_registration(broker):
    """Test user registration"""
    print(f"\n" + "=" * 55)
    print("👤 Testing User Registration")
    print("=" * 55)
    
    try:
        # Registration data
        registration_data = {
            "email_id": "test@example.com",
            "password": "password123",
            "full_name": "Test User",
            "max_trad_per_day": 10,
            "base_stoploss": 5.0,
            "base_target": 10.0,
            "trailing_status": True,
            "trailing_stoploss": 8.0,
            "trailing_target": 15.0,
            "description": "Test Account for Broker Testing"
        }
        
        print("📝 Attempting user registration...")
        print("   (This will initialize database - may take a moment...)")
        
        start_time = time.time()
        response = await broker.registration(registration_data)
        reg_time = time.time() - start_time
        
        if response and response.data:
            print(f"✅ Registration successful! ({reg_time:.3f}s)")
            print(f"   User: {response.data['user']['full_name']}")
            print(f"   Email: {response.data['user']['email_id']}")
            print(f"   Account ID: {response.data['user']['account_id']}")
            return True
        else:
            message = response.message if response else "No response received"
            print(f"❌ Registration failed: {message} ({reg_time:.3f}s)")
            return False
            
    except Exception as e:
        print(f"❌ Registration error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def test_login(broker):
    """Test user login"""
    print(f"\n" + "=" * 55)
    print("🔐 Testing User Login")
    print("=" * 55)
    
    try:
        # Login data
        login_data = {
            "email_id": "test@example.com",
            "password": "password123"
        }
        
        print("🔑 Attempting user login...")
        
        start_time = time.time()
        response = await broker.login(login_data)
        login_time = time.time() - start_time
        
        if response and response.data:
            print(f"✅ Login successful! ({login_time:.3f}s)")
            print(f"   User: {response.data['user']['full_name']}")
            print(f"   Session ID: {response.data['session_id']}")
            print(f"   Access Token: {response.data['access_token'][:20]}...")
            return True
        else:
            message = response.message if response else "No response received"
            print(f"❌ Login failed: {message} ({login_time:.3f}s)")
            return False
            
    except Exception as e:
        print(f"❌ Login error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def test_account_details(broker):
    """Test getting account details"""
    print(f"\n" + "=" * 55)
    print("📊 Testing Account Details")
    print("=" * 55)
    
    try:
        print("📋 Fetching account details...")
        response = await broker.get_account_details()
        
        if response.data:
            account = response.data['account']
            print("✅ Account details retrieved!")
            print(f"   Name: {account['full_name']}")
            print(f"   Balance: ₹{account['balance']}")
            print(f"   Max Trades/Day: {account['max_trad_per_day']}")
            print(f"   Email Verified: {account['email_verified']}")
            return True
        else:
            print(f"❌ Failed to get account details: {response.message}")
            return False
            
    except Exception as e:
        print(f"❌ Account details error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run all tests - Mixed sync/async approach"""
    test_results = []
    
    # Test 1: Basic functionality (SYNC - fast)
    broker = test_basic_functionality()
    if broker:
        test_results.append(("Basic Functionality", True))
        
        # Test 2: Registration
        reg_success = await test_registration(broker)
        test_results.append(("Registration", reg_success))
        
        # Test 3: Login
        login_success = await test_login(broker)
        test_results.append(("Login", login_success))
        
        # Test 4: Account Details (only if login successful)
        if login_success:
            account_success = await test_account_details(broker)
            test_results.append(("Account Details", account_success))
        
    else:
        test_results.append(("Basic Functionality", False))
    
    # Print summary
    print(f"\n" + "=" * 55)
    print("📊 TEST SUMMARY")
    print("=" * 55)
    
    passed = 0
    for test_name, result in test_results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Results: {passed}/{len(test_results)} tests passed")
    
    if passed == len(test_results):
        print("🎉 All tests passed! Broker is working perfectly.")
        return True
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        return False

if __name__ == "__main__":
    try:
        result = asyncio.run(main())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n⏹️  Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)