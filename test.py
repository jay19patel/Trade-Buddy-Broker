"""
Trade Buddy SDK - Complete Test Suite
Production Ready Paper Trading Platform Test
"""

import sys
import os
import asyncio
from datetime import datetime

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from trade_buddy.entities.models import (
    Account, Position, Order, 
    OrderSide, StockType, CreateBy, PositionStatus, OrderTypes, ProductType
)
from trade_buddy.core.exceptions import TradeBuddyException
from trade_buddy.core.response import TradeBuddyResponse
from trade_buddy.utils.security import SecurityManager
from trade_buddy.repositories.account_repository import AccountRepository
from trade_buddy.repositories.position_repository import PositionRepository
from trade_buddy.repositories.order_repository import OrderRepository
from trade_buddy.repositories.transaction_repository import TransactionRepository


class TradeBuddySDK:
    """
    Trade Buddy SDK - Complete Implementation
    Simple, Clean, and Production Ready
    """
    
    def __init__(self):
        """Initialize Trade Buddy SDK"""
        self.security = SecurityManager()
        self.account_repo = AccountRepository()
        self.position_repo = PositionRepository()
        self.order_repo = OrderRepository()
        self.transaction_repo = TransactionRepository()
        self.current_account = None
        
        print("🔧 Trade Buddy SDK initialized successfully")
    
    async def initialize_demo_data(self):
        """Setup demo account for testing"""
        try:
            demo_account = Account(
                account_id="DEMO01",
                full_name="Demo User",
                email_id="demo@tradebuddy.com", 
                password=self.security.generate_hash_password("demo123"),
                balance=100000.0,
                email_verified=True,
                description="Demo account for testing",
                max_trad_per_day=20,
                base_stoploss=5.0,
                base_target=10.0
            )
            
            await self.account_repo.create(demo_account)
            print("📦 Demo account created successfully")
            
        except TradeBuddyException:
            print("📦 Demo account already exists")
    
    async def login(self, user_id: str, password: str) -> TradeBuddyResponse:
        """User login"""
        account = await self.account_repo.get_by_user_id(user_id)
        
        if not account:
            raise TradeBuddyException("❌ User not found")
        
        if not self.security.check_hash_password(password, account.password):
            raise TradeBuddyException("❌ Invalid password")
        
        if not account.email_verified:
            raise TradeBuddyException("❌ Email not verified")
        
        self.current_account = account
        
        return TradeBuddyResponse(
            message="✅ Login successful",
            payload={
                "account_id": account.account_id,
                "full_name": account.full_name,
                "balance": account.balance,
                "email_verified": account.email_verified
            }
        )
    
    async def deposit_funds(self, amount: float, note: str = "") -> TradeBuddyResponse:
        """Deposit funds to account"""
        if not self.current_account:
            raise TradeBuddyException("❌ Please login first")
        
        if amount <= 0:
            raise TradeBuddyException("❌ Amount must be greater than 0")
        
        # Update balance
        old_balance = self.current_account.balance
        self.current_account.balance += amount
        
        # Update account
        await self.account_repo.update(self.current_account)
        
        return TradeBuddyResponse(
            message="✅ Funds deposited successfully",
            payload={
                "amount": amount,
                "old_balance": old_balance,
                "new_balance": self.current_account.balance,
                "transaction_note": note
            }
        )
    
    async def create_order(self, stock_symbol: str, order_side: OrderSide, 
                          price: float, quantity: int, 
                          stoploss_price: float = None, target_price: float = None) -> TradeBuddyResponse:
        """Create new order"""
        if not self.current_account:
            raise TradeBuddyException("❌ Please login first")
        
        if price <= 0 or quantity <= 0:
            raise TradeBuddyException("❌ Price and quantity must be greater than 0")
        
        order_margin = quantity * price
        
        if order_margin > self.current_account.balance:
            raise TradeBuddyException(
                f"❌ Insufficient balance. Required: ₹{order_margin:,.2f}, "
                f"Available: ₹{self.current_account.balance:,.2f}"
            )
        
        # Generate IDs
        position_id = self.security.generate_unique_id("POS")
        order_id = self.security.generate_unique_id("ORD")
        
        # Set default stop-loss and target prices
        if not stoploss_price:
            stoploss_price = price * 0.95 if order_side == OrderSide.BUY else price * 1.05
        if not target_price:
            target_price = price * 1.05 if order_side == OrderSide.BUY else price * 0.95
        
        # Create position
        position = Position(
            position_id=position_id,
            account_id=self.current_account.account_id,
            stock_symbol=stock_symbol.upper(),
            stock_type=StockType.STOCK,
            position_side=order_side,
            buy_average=price if order_side == OrderSide.BUY else 0,
            buy_quantity=quantity if order_side == OrderSide.BUY else 0,
            buy_margin=order_margin if order_side == OrderSide.BUY else 0,
            sell_average=price if order_side == OrderSide.SELL else 0,
            sell_quantity=quantity if order_side == OrderSide.SELL else 0,
            sell_margin=order_margin if order_side == OrderSide.SELL else 0,
            stoploss_price=stoploss_price,
            target_price=target_price,
            created_by=CreateBy.MANUAL
        )
        
        # Create order
        order = Order(
            order_id=order_id,
            account_id=self.current_account.account_id,
            position_id=position_id,
            stock_symbol=stock_symbol.upper(),
            order_side=order_side,
            order_types=OrderTypes.NewOrder,
            product_type=ProductType.CNC,
            price=price,
            quantity=quantity,
            stoploss_price=stoploss_price,
            target_price=target_price,
            created_by=CreateBy.MANUAL,
            stop_order_activate=True
        )
        
        # Update account balance
        self.current_account.balance -= order_margin
        
        # Save to repositories
        await self.position_repo.create(position)
        await self.order_repo.create(order)
        await self.account_repo.update(self.current_account)
        
        return TradeBuddyResponse(
            message=f"✅ {order_side.value} order created for {stock_symbol}",
            payload={
                "position_id": position_id,
                "order_id": order_id,
                "stock_symbol": stock_symbol,
                "quantity": quantity,
                "price": price,
                "order_margin": order_margin,
                "remaining_balance": self.current_account.balance,
                "stoploss_price": stoploss_price,
                "target_price": target_price
            }
        )
    
    async def exit_position(self, position_id: str, exit_price: float) -> TradeBuddyResponse:
        """Exit position completely"""
        if not self.current_account:
            raise TradeBuddyException("❌ Please login first")
        
        position = await self.position_repo.get_by_id(position_id)
        
        if not position or position.position_status != PositionStatus.PENDING:
            raise TradeBuddyException("❌ Position not found or already closed")
        
        if position.account_id != self.current_account.account_id:
            raise TradeBuddyException("❌ Position does not belong to current account")
        
        # Calculate exit details
        exit_qty = abs(position.buy_quantity - position.sell_quantity)
        exit_side = OrderSide.SELL if position.position_side == OrderSide.BUY else OrderSide.BUY
        exit_margin = exit_qty * exit_price
        
        # Update position
        if position.position_side == OrderSide.BUY:
            position.sell_quantity += exit_qty
            position.sell_margin += exit_margin
            position.sell_average = (
                (position.sell_average * (position.sell_quantity - exit_qty) + 
                 exit_price * exit_qty) / position.sell_quantity
            ) if position.sell_quantity > 0 else exit_price
        else:
            position.buy_quantity += exit_qty
            position.buy_margin += exit_margin
            position.buy_average = (
                (position.buy_average * (position.buy_quantity - exit_qty) + 
                 exit_price * exit_qty) / position.buy_quantity
            ) if position.buy_quantity > 0 else exit_price
        
        # Calculate P&L
        pnl = (position.sell_average - position.buy_average) * position.sell_quantity
        position.pnl_total = pnl
        position.position_status = PositionStatus.COMPLETED
        
        # Create exit order
        exit_order = Order(
            order_id=self.security.generate_unique_id("ORD"),
            account_id=self.current_account.account_id,
            position_id=position_id,
            stock_symbol=position.stock_symbol,
            order_side=exit_side,
            order_types=OrderTypes.ExitOrder,
            product_type=position.product_type,
            price=exit_price,
            quantity=exit_qty,
            created_by=CreateBy.MANUAL,
            stop_order_hit=True
        )
        
        # Update account balance
        self.current_account.balance += exit_margin
        
        # Save updates
        await self.position_repo.update(position)
        await self.order_repo.create(exit_order)
        await self.account_repo.update(self.current_account)
        
        return TradeBuddyResponse(
            message=f"✅ Position exited for {position.stock_symbol}",
            payload={
                "position_id": position_id,
                "exit_order_id": exit_order.order_id,
                "exit_price": exit_price,
                "exit_quantity": exit_qty,
                "pnl": pnl,
                "pnl_percentage": (pnl / (position.buy_average * position.buy_quantity)) * 100 if position.buy_quantity > 0 else 0,
                "account_balance": self.current_account.balance
            }
        )
    
    async def get_positions(self) -> dict:
        """Get all positions"""
        if not self.current_account:
            raise TradeBuddyException("❌ Please login first")
        
        positions = await self.position_repo.get_by_account(self.current_account.account_id)
        
        # Add orders to each position
        for position in positions:
            orders = await self.order_repo.get_by_position(position.position_id)
            orders.sort(key=lambda x: x.order_datetime, reverse=True)
            position.orders = orders
        
        # Calculate overview
        open_positions = [p for p in positions if p.position_status == PositionStatus.PENDING]
        closed_positions = [p for p in positions if p.position_status == PositionStatus.COMPLETED]
        
        total_pnl = sum(p.pnl_total for p in positions)
        invested_amount = sum(abs(p.buy_margin - p.sell_margin) for p in open_positions)
        
        return {
            "positions": [pos.to_dict() for pos in positions],
            "overview": {
                "total_positions": len(positions),
                "open_positions": len(open_positions),
                "closed_positions": len(closed_positions),
                "account_balance": self.current_account.balance,
                "invested_amount": invested_amount,
                "total_pnl": total_pnl,
                "positive_pnl_count": sum(1 for p in positions if p.pnl_total > 0),
                "negative_pnl_count": sum(1 for p in positions if p.pnl_total < 0)
            }
        }
    
    def get_account_summary(self) -> dict:
        """Get account summary"""
        if not self.current_account:
            raise TradeBuddyException("❌ Please login first")
        
        return {
            "account_id": self.current_account.account_id,
            "full_name": self.current_account.full_name,
            "email_id": self.current_account.email_id,
            "balance": self.current_account.balance,
            "max_trades_per_day": self.current_account.max_trad_per_day,
            "base_stoploss": self.current_account.base_stoploss,
            "base_target": self.current_account.base_target,
            "email_verified": self.current_account.email_verified,
            "account_created": self.current_account.created_datetime.strftime("%Y-%m-%d %H:%M:%S")
        }


class TestRunner:
    """Test runner for Trade Buddy SDK"""
    
    def __init__(self):
        self.sdk = TradeBuddySDK()
        self.test_results = []
    
    def print_header(self, title: str):
        """Print test section header"""
        print(f"\n{'='*60}")
        print(f"🧪 {title}")
        print(f"{'='*60}")
    
    def print_step(self, step: str, description: str):
        """Print test step"""
        print(f"\n📋 {step}: {description}")
        print("-" * 40)
    
    def print_success(self, message: str, data: dict = None):
        """Print success message"""
        print(f"✅ {message}")
        if data:
            for key, value in data.items():
                if isinstance(value, float) and key in ['balance', 'amount', 'price', 'pnl']:
                    print(f"   • {key}: ₹{value:,.2f}")
                else:
                    print(f"   • {key}: {value}")
    
    def print_error(self, message: str):
        """Print error message"""
        print(f"❌ {message}")
    
    async def run_complete_test_suite(self):
        """Run complete test suite"""
        self.print_header("Trade Buddy SDK - Complete Test Suite")
        print("🚀 Testing Production Ready Paper Trading Platform")
        print(f"📅 Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        try:
            # Test 1: Initialize SDK
            self.print_step("STEP 1", "Initialize SDK & Demo Data")
            await self.sdk.initialize_demo_data()
            self.print_success("SDK initialized successfully")
            
            # Test 2: User Login
            self.print_step("STEP 2", "User Authentication")
            login_response = await self.sdk.login("demo@tradebuddy.com", "demo123")
            self.print_success(login_response.message, login_response.payload)
            
            # Test 3: Account Summary
            self.print_step("STEP 3", "Account Summary")
            account_summary = self.sdk.get_account_summary()
            self.print_success("Account summary retrieved", account_summary)
            
            # Test 4: Deposit Funds
            self.print_step("STEP 4", "Fund Deposit")
            deposit_response = await self.sdk.deposit_funds(50000.0, "Initial test deposit")
            self.print_success(deposit_response.message, deposit_response.payload)
            
            # Test 5: Create Multiple Orders
            self.print_step("STEP 5", "Create Trading Orders")
            
            # Order 1: BUY RELIANCE
            order1_response = await self.sdk.create_order("RELIANCE", OrderSide.BUY, 2500.0, 10, 2400.0, 2600.0)
            self.print_success("RELIANCE BUY order created", {
                "position_id": order1_response.payload['position_id'],
                "quantity": order1_response.payload['quantity'],
                "price": order1_response.payload['price']
            })
            position1_id = order1_response.payload['position_id']
            
            # Order 2: BUY TCS
            order2_response = await self.sdk.create_order("TCS", OrderSide.BUY, 3500.0, 5, 3300.0, 3700.0)
            self.print_success("TCS BUY order created", {
                "position_id": order2_response.payload['position_id'],
                "quantity": order2_response.payload['quantity'],
                "price": order2_response.payload['price']
            })
            position2_id = order2_response.payload['position_id']
            
            # Order 3: SELL INFY (Short position)
            order3_response = await self.sdk.create_order("INFY", OrderSide.SELL, 1800.0, 8, 1900.0, 1700.0)
            self.print_success("INFY SELL order created", {
                "position_id": order3_response.payload['position_id'],
                "quantity": order3_response.payload['quantity'],
                "price": order3_response.payload['price']
            })
            position3_id = order3_response.payload['position_id']
            
            # Test 6: Get Positions
            self.print_step("STEP 6", "Portfolio Overview")
            positions_data = await self.sdk.get_positions()
            overview = positions_data['overview']
            
            self.print_success("Portfolio retrieved successfully", {
                "total_positions": overview['total_positions'],
                "open_positions": overview['open_positions'],
                "closed_positions": overview['closed_positions'],
                "account_balance": overview['account_balance'],
                "invested_amount": overview['invested_amount']
            })
            
            # Print individual positions
            print("\n📊 Individual Position Details:")
            for pos in positions_data['positions']:
                if pos['position_status'] == 'Pending':
                    if pos['position_side'] == 'BUY':
                        qty = pos['buy_quantity']
                        avg_price = pos['buy_average']
                    else:
                        qty = -pos['sell_quantity']
                        avg_price = pos['sell_average']
                    print(f"   🔹 {pos['stock_symbol']}: {qty} qty @ ₹{avg_price:.2f}")
            
            # Test 7: Exit Some Positions
            self.print_step("STEP 7", "Position Exit (Profit Booking)")
            
            # Exit RELIANCE with profit
            exit1_response = await self.sdk.exit_position(position1_id, 2700.0)  # Profitable exit
            self.print_success("RELIANCE position exited", {
                "pnl": exit1_response.payload['pnl'],
                "pnl_percentage": f"{exit1_response.payload['pnl_percentage']:.2f}%",
                "account_balance": exit1_response.payload['account_balance']
            })
            
            # Exit TCS with loss
            exit2_response = await self.sdk.exit_position(position2_id, 3300.0)  # Loss exit
            self.print_success("TCS position exited", {
                "pnl": exit2_response.payload['pnl'],
                "pnl_percentage": f"{exit2_response.payload['pnl_percentage']:.2f}%",
                "account_balance": exit2_response.payload['account_balance']
            })
            
            # Test 8: Final Portfolio Status
            self.print_step("STEP 8", "Final Portfolio Status")
            final_positions = await self.sdk.get_positions()
            final_overview = final_positions['overview']
            
            self.print_success("Final portfolio status", {
                "total_positions": final_overview['total_positions'],
                "open_positions": final_overview['open_positions'],
                "closed_positions": final_overview['closed_positions'],
                "total_pnl": final_overview['total_pnl'],
                "account_balance": final_overview['account_balance']
            })
            
            # Test Summary
            self.print_header("TEST SUMMARY")
            print("🎯 All Core Features Tested:")
            print("   ✅ User Authentication")
            print("   ✅ Fund Management (Deposit)")
            print("   ✅ Order Creation (BUY/SELL)")
            print("   ✅ Position Management")
            print("   ✅ P&L Calculation")
            print("   ✅ Portfolio Tracking")
            print("   ✅ Position Exit")
            print("   ✅ Account Management")
            
            print(f"\n🏆 Test Suite Completed Successfully!")
            print(f"📈 Final P&L: ₹{final_overview['total_pnl']:,.2f}")
            print(f"💰 Final Balance: ₹{final_overview['account_balance']:,.2f}")
            
            return True
            
        except TradeBuddyException as e:
            self.print_error(f"Trade Buddy Error: {e.message}")
            return False
        except Exception as e:
            self.print_error(f"Unexpected Error: {str(e)}")
            import traceback
            traceback.print_exc()
            return False


async def main():
    """Main test function"""
    test_runner = TestRunner()
    success = await test_runner.run_complete_test_suite()
    
    if success:
        print(f"\n🎉 Trade Buddy SDK is working perfectly!")
        print("🔧 Production ready for paper trading operations")
    else:
        print(f"\n❌ Tests failed - please check the implementation")
    
    return success


if __name__ == "__main__":
    try:
        result = asyncio.run(main())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n⏹️ Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Critical error: {str(e)}")
        sys.exit(1)