#!/usr/bin/env python3
"""
Fast Test - Test if object creation is now fast
"""

import sys
import os
import time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    print("⚡ Testing Fast Object Creation")
    print("=" * 35)
    
    try:
        # Import test
        start_time = time.time()
        print("1. Importing TradeBuddy...")
        from trade_buddy.broker import TradeBuddy
        import_time = time.time() - start_time
        print(f"   ✅ Import took: {import_time:.3f}s")
        
        # Object creation test
        start_time = time.time()
        print("\n2. Creating TradeBuddy object...")
        broker = TradeBuddy()
        creation_time = time.time() - start_time
        print(f"   ✅ Object creation took: {creation_time:.3f}s")
        
        # Basic property test
        start_time = time.time()
        print(f"\n3. Testing .test variable...")
        test_value = broker.test
        access_time = time.time() - start_time
        print(f"   ✅ broker.test = '{test_value}' (took: {access_time:.3f}s)")
        
        # Property access test (this might be slow)
        start_time = time.time()
        print(f"\n4. Testing property access...")
        try:
            service_factory = broker.service_factory
            property_time = time.time() - start_time
            if service_factory:
                print(f"   ✅ Service factory loaded (took: {property_time:.3f}s)")
            else:
                print(f"   ⚠️  Service factory is None (took: {property_time:.3f}s)")
        except Exception as e:
            property_time = time.time() - start_time
            print(f"   ⚠️  Property access failed: {e} (took: {property_time:.3f}s)")
        
        print(f"\n" + "=" * 35)
        
        # Speed analysis
        if creation_time < 0.1:
            print("🚀 EXCELLENT: Object creation is super fast!")
        elif creation_time < 0.5:
            print("✅ GOOD: Object creation is acceptable")
        else:
            print("⚠️  SLOW: Object creation is still slow")
            
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)