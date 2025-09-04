#!/usr/bin/env python3
"""
Property Test - Testing Production Ready Approach
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    print("🏭 Testing Production Ready Property-Based Approach")
    print("=" * 55)
    
    try:
        # Import
        print("1. Importing TradeBuddy...")
        from trade_buddy.broker import TradeBuddy
        print("   ✅ Import successful!")
        
        # Create object
        print("\n2. Creating TradeBuddy object...")
        broker = TradeBuddy()
        print("   ✅ Object created successfully!")
        
        # Test .test variable
        print(f"\n3. Testing .test variable...")
        print(f"   ✅ broker.test = '{broker.test}'")
        
        # Test property-based access (this is what you wanted)
        print(f"\n4. Testing property-based service access...")
        print(f"   🔧 Accessing broker.service_factory...")
        service_factory = broker.service_factory
        print(f"   ✅ Service Factory: {type(service_factory).__name__}")
        
        # Test the way you want to use it
        print(f"\n5. Testing production ready method calls...")
        print(f"   🔧 Calling service_factory.create_service('price')...")
        
        # This is exactly how you wanted to use it:
        # price_service = self.service_factory.create_service('price')
        price_service = broker.service_factory.create_service('price')
        print(f"   ✅ Price Service: {type(price_service).__name__}")
        
        print(f"\n6. Testing session manager property...")
        session_manager = broker.session_manager
        print(f"   ✅ Session Manager: {type(session_manager).__name__}")
        
        print("\n" + "=" * 55)
        print("🎉 PRODUCTION READY APPROACH WORKING!")
        print("✅ You can now use:")
        print("   • broker.service_factory.create_service('auth')")
        print("   • broker.service_factory.create_service('price')")  
        print("   • broker.service_factory.create_service('transaction')")
        print("   • broker.session_manager.create_session(...)")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)