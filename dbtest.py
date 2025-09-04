#!/usr/bin/env python3
"""
Database Test File - Testing Trade Buddy Database and Models
Tests database connection, table creation, and CRUD operations
"""

import asyncio
import sys
from datetime import datetime, timedelta
from trade_buddy.core.database import DatabaseManager, get_database_manager, initialize_database
from trade_buddy.entities.models import Account, Transaction, Session, TransactionType


async def test_database_connection():
    """Test database connection and table creation"""
    print("=" * 50)
    print("=Testing Database Connection")
    print("=" * 50)
    
    try:
        # Initialize database
        print("Initializing database...")
        await initialize_database()
        print(" Database initialized successfully!")
        
        # Get database manager
        db = get_database_manager()
        print(f" Database URL: {db.database_url}")
        
        return True
    except Exception as e:
        print(f"L Database connection failed: {str(e)}")
        return False


async def test_account_operations():
    """Test Account model CRUD operations"""
    print("\n" + "=" * 50)
    print("=d Testing Account Operations")
    print("=" * 50)
    
    db = get_database_manager()
    
    try:
        # Create test account
        test_account = Account(
            account_id="test_acc_001",
            full_name="Test User",
            email_id="test@example.com",
            password="hashed_password",
            balance=1000.0,
            max_trad_per_day=10,
            base_stoploss=5.0,
            base_target=10.0,
            trailing_status=True,
            trailing_stoploss=8.0,
            trailing_target=15.0,
            description="Test Account for Database Testing"
        )
        
        # Insert account
        async for session in db.get_session():
            session.add(test_account)
            await session.commit()
            print(" Account created successfully!")
            break
        
        # Read account
        async for session in db.get_session():
            from sqlalchemy import select
            result = await session.execute(select(Account).where(Account.account_id == "test_acc_001"))
            account = result.scalar_one_or_none()
            
            if account:
                print(f" Account found: {account.full_name} ({account.email_id})")
                print(f"   Balance: �{account.balance}")
                print(f"   Max trades/day: {account.max_trad_per_day}")
            else:
                print("L Account not found")
                return False
            break
        
        return True
        
    except Exception as e:
        print(f"L Account operations failed: {str(e)}")
        return False


async def test_transaction_operations():
    """Test Transaction model operations"""
    print("\n" + "=" * 50)
    print("=� Testing Transaction Operations")
    print("=" * 50)
    
    db = get_database_manager()
    
    try:
        # Create test transactions
        transactions = [
            Transaction(
                transaction_id="txn_001",
                account_id="test_acc_001",
                transaction_type=TransactionType.DEPOSIT.value,
                transaction_amount=500.0,
                transaction_note="Initial deposit"
            ),
            Transaction(
                transaction_id="txn_002",
                account_id="test_acc_001",
                transaction_type=TransactionType.WITHDRAW.value,
                transaction_amount=100.0,
                transaction_note="Test withdrawal"
            )
        ]
        
        # Insert transactions
        async for session in db.get_session():
            for txn in transactions:
                session.add(txn)
            await session.commit()
            print(" Transactions created successfully!")
            break
        
        # Read transactions
        async for session in db.get_session():
            from sqlalchemy import select
            result = await session.execute(select(Transaction).where(Transaction.account_id == "test_acc_001"))
            txns = result.scalars().all()
            
            print(f" Found {len(txns)} transactions:")
            for txn in txns:
                print(f"   {txn.transaction_type}: �{txn.transaction_amount} - {txn.transaction_note}")
            break
        
        return True
        
    except Exception as e:
        print(f"L Transaction operations failed: {str(e)}")
        return False


async def test_session_operations():
    """Test Session model operations"""
    print("\n" + "=" * 50)
    print("= Testing Session Operations")
    print("=" * 50)
    
    db = get_database_manager()
    
    try:
        # Create test session
        test_session = Session(
            session_id="sess_001",
            account_id="test_acc_001",
            jwt_token="fake_jwt_token_123",
            device_info="Test Device",
            ip_address="127.0.0.1",
            expires_at=datetime.now() + timedelta(hours=24)
        )
        
        # Insert session
        async for session in db.get_session():
            session.add(test_session)
            await session.commit()
            print(" Session created successfully!")
            break
        
        # Read session
        async for session in db.get_session():
            from sqlalchemy import select
            result = await session.execute(select(Session).where(Session.account_id == "test_acc_001"))
            user_session = result.scalar_one_or_none()
            
            if user_session:
                print(f" Session found: {user_session.session_id}")
                print(f"   Device: {user_session.device_info}")
                print(f"   Active: {user_session.is_active}")
                print(f"   Expires: {user_session.expires_at}")
            else:
                print("L Session not found")
                return False
            break
        
        return True
        
    except Exception as e:
        print(f"L Session operations failed: {str(e)}")
        return False


async def test_database_cleanup():
    """Test database cleanup operations"""
    print("\n" + "=" * 50)
    print(">� Testing Database Cleanup")
    print("=" * 50)
    
    db = get_database_manager()
    
    try:
        # Test truncate all tables
        await db.truncate_all_tables()
        print(" All tables truncated successfully!")
        
        # Verify tables are empty
        async for session in db.get_session():
            from sqlalchemy import select, func
            
            # Check accounts count
            result = await session.execute(select(func.count(Account.account_id)))
            account_count = result.scalar()
            
            # Check transactions count
            result = await session.execute(select(func.count(Transaction.transaction_id)))
            txn_count = result.scalar()
            
            # Check sessions count
            result = await session.execute(select(func.count(Session.session_id)))
            session_count = result.scalar()
            
            print(f" Tables cleaned - Accounts: {account_count}, Transactions: {txn_count}, Sessions: {session_count}")
            break
        
        return True
        
    except Exception as e:
        print(f"L Database cleanup failed: {str(e)}")
        return False


async def main():
    """Run all database tests"""
    print("=� Starting Trade Buddy Database Tests")
    print("=" * 60)
    
    tests = [
        ("Database Connection", test_database_connection),
        ("Account Operations", test_account_operations),
        ("Transaction Operations", test_transaction_operations),
        ("Session Operations", test_session_operations),
        ("Database Cleanup", test_database_cleanup)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"L {test_name} failed with error: {str(e)}")
            results.append((test_name, False))
    
    # Print summary
    print("\n" + "=" * 60)
    print("=� TEST SUMMARY")
    print("=" * 60)
    
    passed = 0
    for test_name, result in results:
        status = " PASSED" if result else "L FAILED"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n<� Results: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("<� All tests passed! Database is working correctly.")
        return True
    else:
        print("�  Some tests failed. Check the output above for details.")
        return False


if __name__ == "__main__":
    try:
        result = asyncio.run(main())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n�  Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n=� Unexpected error: {str(e)}")
        sys.exit(1)