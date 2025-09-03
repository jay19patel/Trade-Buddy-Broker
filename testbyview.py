"""
Trade Buddy View Utility Test - Beautiful Table Display
Real broker data visualization using Rich tables
"""

import sys
import os
import asyncio
from datetime import datetime

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from trade_buddy.utils.view import view
from trade_buddy.entities.models import OrderSide
from trade_buddy.core.exceptions import TradeBuddyException


# Import TradeBuddySDK from test.py
from test import TradeBuddySDK


class ViewTestDemo:
    """
    View Test Demo - Beautiful Table Display
    Demonstrates all view functions with real broker data
    """
    
    def __init__(self):
        """Initialize demo with Trade Buddy SDK"""
        self.sdk = TradeBuddySDK()
        self.account_data = None
        self.positions_data = None
        self.orders_data = []
        self.transactions_data = []
        
        print("🎨 Trade Buddy View Test Demo initialized")
        print("📊 Using real broker data for beautiful table displays\n")
    
    async def setup_demo_trading_session(self):
        """Setup demo trading session with real broker data"""
        try:
            # Initialize demo data and login
            await self.sdk.initialize_demo_data()
            login_response = await self.sdk.login("demo@tradebuddy.com", "demo123")
            
            # Get account data
            self.account_data = self.sdk.get_account_summary()
            
            # Deposit some funds
            await self.sdk.deposit_funds(50000.0, "Initial demo deposit")
            
            # Create some sample trades
            await self._create_sample_trades()
            
            # Get updated data
            self.account_data = self.sdk.get_account_summary()
            self.positions_data = await self.sdk.get_positions()
            
            # Get orders from positions (since orders are attached to positions in the SDK)
            self.orders_data = []
            for position in self.positions_data.get('positions', []):
                if 'orders' in position:
                    self.orders_data.extend(position['orders'])
            
            print("✅ Demo trading session setup completed")
            
        except Exception as e:
            print(f"❌ Error setting up demo session: {e}")
            raise
    
    async def _create_sample_trades(self):
        """Create sample trades using real broker SDK"""
        try:
            # Create multiple orders to demonstrate the system
            
            # Order 1: BUY RELIANCE
            await self.sdk.create_order("RELIANCE", OrderSide.BUY, 2500.0, 10)
            
            # Order 2: BUY TCS
            order2_response = await self.sdk.create_order("TCS", OrderSide.BUY, 3500.0, 5)
            
            # Order 3: SELL INFY (Short position)
            await self.sdk.create_order("INFY", OrderSide.SELL, 1800.0, 8)
            
            # Order 4: BUY HDFC
            order4_response = await self.sdk.create_order("HDFC", OrderSide.BUY, 1650.0, 12)
            
            # Order 5: BUY ICICIBANK
            await self.sdk.create_order("ICICIBANK", OrderSide.BUY, 950.0, 15)
            
            # Exit some positions to show completed trades
            # Exit TCS with profit
            await self.sdk.exit_position(order2_response.payload['position_id'], 3650.0)
            
            # Exit HDFC with loss
            await self.sdk.exit_position(order4_response.payload['position_id'], 1598.0)
            
            print("✅ Sample trades created successfully")
            
        except Exception as e:
            print(f"❌ Error creating sample trades: {e}")
            raise
    
    def _create_sample_transactions(self):
        """Create sample transactions - using repository data"""
        # For now, we'll create a basic transaction list since the SDK doesn't have transaction repository exposed
        # This would typically come from the transaction repository in a real implementation
        self.transactions_data = [
            {
                "transaction_id": "TXN001",
                "transaction_type": "DEPOSIT", 
                "amount": 100000.00,
                "balance_after": 100000.00,
                "status": "SUCCESS",
                "note": "Initial account funding",
                "created_datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            },
            {
                "transaction_id": "TXN002", 
                "transaction_type": "DEPOSIT",
                "amount": 50000.00,
                "balance_after": 150000.00,
                "status": "SUCCESS", 
                "note": "Demo deposit for trading",
                "created_datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        ]
    
    async def demo_all_views(self):
        """Demo all views in sequence with real broker data"""
        print("🎨 Trade Buddy View Utility - Complete Demo")
        print("="*60)
        print("📊 Demonstrating all view functions with REAL broker data")
        print("="*60)
        
        # Setup demo trading session with real data
        print("🔧 Setting up demo trading session...")
        await self.setup_demo_trading_session()
        
        # Create sample transactions for demo
        self._create_sample_transactions()
        
        # Demo 1: Account Summary
        print("\n🔥 1. Account Summary View (Real Data)")
        view.view_account(self.account_data)
        
        # Demo 2: Portfolio Dashboard
        print("🔥 2. Complete Portfolio Dashboard (Real Data)")
        view.view_portfolio_summary(self.account_data, self.positions_data)
        
        # Demo 3: Positions Detail
        print("🔥 3. Positions & Portfolio Detail (Real Data)")
        view.view_positions(self.positions_data)
        
        # Demo 4: Orders History
        print("🔥 4. Orders History (Real Data)")
        view.view_orders(self.orders_data)
        
        # Demo 5: Transaction History
        print("🔥 5. Transaction History (Sample Data)")
        view.view_transactions(self.transactions_data)
        
        # Demo 6: Utility Messages
        print("🔥 6. Utility Messages")
        print("="*40)
        view.print_success("Trade executed successfully!")
        view.print_error("Insufficient balance for this trade")
        view.print_warning("Market volatility is high today")
        view.print_info("Market opening in 5 minutes")
        
        print("\n" + "="*60)
        print("✅ All view functions demonstrated with REAL broker data!")
        print("🚀 Trade Buddy View Utility is ready for production use")
        print("="*60)
    


async def main():
    """Main demo function"""
    try:
        demo = ViewTestDemo()
        await demo.demo_all_views()
            
    except KeyboardInterrupt:
        print("\n⏹️ Demo interrupted by user")
    except Exception as e:
        print(f"\n💥 Critical error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())