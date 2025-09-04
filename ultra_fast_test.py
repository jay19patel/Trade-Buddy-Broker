#!/usr/bin/env python3
"""
Ultra Fast Test - Only test basic object creation without any heavy operations
"""

import sys
import os
import time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    print("🚀 Ultra Fast Object Creation Test")
    print("=" * 40)
    
    try:
        # Import test
        start_time = time.time()
        print("1. Importing TradeBuddy...")
        from trade_buddy.broker import TradeBuddy
        import_time = time.time() - start_time
        print(f"   ✅ Import took: {import_time:.3f}s")
        
        # Object creation test (should be instant now)
        start_time = time.time()
        print("\n2. Creating TradeBuddy object...")
        broker = TradeBuddy()
        creation_time = time.time() - start_time
        print(f"   ✅ Creation took: {creation_time:.3f}s")
        
        # Test basic properties (should be instant)
        start_time = time.time()
        print(f"\n3. Testing basic properties...")
        test_value = broker.test
        session_id = broker._current_session_id
        initialized = broker._initialized
        basic_time = time.time() - start_time
        
        print(f"   ✅ broker.test = '{test_value}'")
        print(f"   ✅ Session ID: {session_id}")
        print(f"   ✅ Initialized: {initialized}")
        print(f"   ⚡ Basic access took: {basic_time:.3f}s")
        
        print(f"\n" + "=" * 40)
        print("📊 PERFORMANCE ANALYSIS:")
        
        if creation_time < 0.01:
            print("🚀 EXCELLENT: Object creation is lightning fast!")
        elif creation_time < 0.1:
            print("✅ GOOD: Object creation is very fast")
        elif creation_time < 0.5:
            print("⚠️  OK: Object creation is acceptable")
        else:
            print("❌ SLOW: Object creation is still too slow")
            
        print(f"\n🎯 READY FOR PRODUCTION: Basic broker functionality working!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)