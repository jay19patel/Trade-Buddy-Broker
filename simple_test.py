#!/usr/bin/env python3
"""
Simple test for TBResponse and basic imports
"""

import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test if all imports work"""
    print("Testing imports...")
    
    try:
        from trade_buddy.entities.response_schemas import TBResponse, UserData
        print("✅ Response schemas import successful")
        
        # Test TBResponse
        response = TBResponse(message="Test", data={"test": True})
        print(f"✅ TBResponse created: {response.message}")
        print(f"✅ Response data: {response.data}")
        
        # Test serialization
        response_dict = response.model_dump()
        print(f"✅ Serialization: {type(response_dict)}")
        
    except Exception as e:
        print(f"❌ Response schemas import failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    try:
        from trade_buddy.core.database import DatabaseManager
        print("✅ Database manager import successful")
        
    except Exception as e:
        print(f"❌ Database manager import failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    try:
        from trade_buddy.entities.models import Account, Position, Order
        print("✅ SQLModel entities import successful")
        
    except Exception as e:
        print(f"❌ SQLModel entities import failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    try:
        from trade_buddy.broker import TradeBuddy
        print("✅ TradeBuddy broker import successful")
        
        broker = TradeBuddy()
        print("✅ Broker instance created")
        
    except Exception as e:
        print(f"❌ TradeBuddy broker import failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    print("🔬 Simple Import Test")
    print("=" * 30)
    
    success = test_imports()
    
    if success:
        print("\n✅ All imports successful!")
        print("🎉 Implementation ready for use!")
    else:
        print("\n❌ Some imports failed!")
        print("🔧 Please check the errors above")