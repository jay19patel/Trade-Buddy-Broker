"""
Trade Buddy View Utility - Beautiful Table Visualization
Rich-based table formatter for account, positions, transactions display
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from decimal import Decimal

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.columns import Columns
from rich import box
from rich.align import Align


class TradeBuddyView:
    """
    Trade Buddy View Utility
    Beautiful table visualization using Rich library
    """
    
    def __init__(self):
        """Initialize view utility"""
        self.console = Console()
    
    def view_account(self, account_data: Dict[str, Any]) -> None:
        """
        Display account details in beautiful table format
        
        Args:
            account_data: Dictionary containing account information
        """
        # Create account summary table
        account_table = Table(
            title="💰 Account Summary",
            show_header=True,
            header_style="bold magenta",
            box=box.ROUNDED,
            title_style="bold cyan"
        )
        
        account_table.add_column("Field", style="cyan", no_wrap=True, width=20)
        account_table.add_column("Value", style="white", width=30)
        
        # Format balance with currency
        balance = account_data.get('balance', 0)
        balance_color = "green" if balance > 0 else "red" if balance < 0 else "yellow"
        formatted_balance = f"₹{balance:,.2f}"
        
        # Add account details
        account_table.add_row("Account ID", str(account_data.get('account_id', 'N/A')))
        account_table.add_row("Full Name", str(account_data.get('full_name', 'N/A')))
        account_table.add_row("Email", str(account_data.get('email_id', 'N/A')))
        account_table.add_row("Balance", f"[{balance_color}]{formatted_balance}[/{balance_color}]")
        account_table.add_row("Max Trades/Day", str(account_data.get('max_trades_per_day', 'N/A')))
        account_table.add_row("Base Stoploss", f"{account_data.get('base_stoploss', 0)}%")
        account_table.add_row("Base Target", f"{account_data.get('base_target', 0)}%")
        
        email_verified = account_data.get('email_verified', False)
        status_color = "green" if email_verified else "red"
        status_text = "✅ Verified" if email_verified else "❌ Not Verified"
        account_table.add_row("Email Status", f"[{status_color}]{status_text}[/{status_color}]")
        
        account_table.add_row("Created", str(account_data.get('account_created', 'N/A')))
        
        # Display table
        self.console.print()
        self.console.print(account_table)
        self.console.print()
    
    def view_positions(self, positions_data: Dict[str, Any]) -> None:
        """
        Display positions in beautiful table format with portfolio overview
        
        Args:
            positions_data: Dictionary containing positions and overview data
        """
        positions = positions_data.get('positions', [])
        overview = positions_data.get('overview', {})
        
        # Portfolio Overview Panel
        overview_content = [
            f"📊 Total Positions: {overview.get('total_positions', 0)}",
            f"📈 Open Positions: {overview.get('open_positions', 0)}",
            f"📉 Closed Positions: {overview.get('closed_positions', 0)}",
            f"💰 Account Balance: ₹{overview.get('account_balance', 0):,.2f}",
            f"💸 Invested Amount: ₹{overview.get('invested_amount', 0):,.2f}",
        ]
        
        total_pnl = overview.get('total_pnl', 0)
        pnl_color = "green" if total_pnl > 0 else "red" if total_pnl < 0 else "yellow"
        overview_content.append(f"📊 Total P&L: [{pnl_color}]₹{total_pnl:,.2f}[/{pnl_color}]")
        
        overview_panel = Panel(
            "\n".join(overview_content),
            title="💼 Portfolio Overview",
            border_style="blue",
            padding=(1, 2)
        )
        
        # Positions Table
        positions_table = Table(
            title="📈 Positions Detail",
            show_header=True,
            header_style="bold yellow",
            box=box.HEAVY_HEAD,
            title_style="bold green"
        )
        
        positions_table.add_column("Symbol", style="cyan", no_wrap=True, width=8)
        positions_table.add_column("Side", style="white", width=6)
        positions_table.add_column("Qty", style="white", width=6, justify="right")
        positions_table.add_column("Avg Price", style="white", width=10, justify="right")
        positions_table.add_column("Current", style="white", width=10, justify="right")
        positions_table.add_column("P&L", style="white", width=12, justify="right")
        positions_table.add_column("P&L %", style="white", width=8, justify="right")
        positions_table.add_column("Status", style="white", width=10)
        
        # Add position rows
        for pos in positions:
            symbol = pos.get('stock_symbol', 'N/A')
            side = pos.get('position_side', 'N/A')
            
            # Calculate quantity and price based on side
            if side == 'BUY':
                quantity = pos.get('buy_quantity', 0)
                avg_price = pos.get('buy_average', 0)
                current_price = pos.get('sell_average', avg_price)
            else:
                quantity = -pos.get('sell_quantity', 0)  # Negative for short
                avg_price = pos.get('sell_average', 0)
                current_price = pos.get('buy_average', avg_price)
            
            pnl = pos.get('pnl_total', 0)
            
            # Calculate P&L percentage
            if avg_price > 0:
                pnl_percentage = (pnl / (abs(quantity) * avg_price)) * 100
            else:
                pnl_percentage = 0
            
            # Color coding for P&L
            pnl_color = "green" if pnl > 0 else "red" if pnl < 0 else "yellow"
            
            # Side color coding
            side_color = "green" if side == 'BUY' else "red"
            
            # Status color coding
            status = pos.get('position_status', 'Unknown')
            status_color = "green" if status == 'Completed' else "yellow" if status == 'Pending' else "white"
            
            positions_table.add_row(
                symbol,
                f"[{side_color}]{side}[/{side_color}]",
                str(abs(quantity)),
                f"₹{avg_price:,.2f}",
                f"₹{current_price:,.2f}",
                f"[{pnl_color}]₹{pnl:,.2f}[/{pnl_color}]",
                f"[{pnl_color}]{pnl_percentage:+.2f}%[/{pnl_color}]",
                f"[{status_color}]{status}[/{status_color}]"
            )
        
        # Display tables
        self.console.print()
        self.console.print(overview_panel)
        self.console.print()
        
        if positions:
            self.console.print(positions_table)
        else:
            empty_panel = Panel(
                "No positions found",
                title="📈 Positions",
                border_style="yellow",
                padding=(1, 2)
            )
            self.console.print(empty_panel)
        self.console.print()
    
    def view_orders(self, orders: List[Dict[str, Any]]) -> None:
        """
        Display orders in beautiful table format
        
        Args:
            orders: List of order dictionaries
        """
        if not orders:
            empty_panel = Panel(
                "No orders found",
                title="📋 Orders",
                border_style="yellow",
                padding=(1, 2)
            )
            self.console.print(empty_panel)
            return
        
        orders_table = Table(
            title="📋 Orders History",
            show_header=True,
            header_style="bold blue",
            box=box.HEAVY_HEAD,
            title_style="bold magenta"
        )
        
        orders_table.add_column("Order ID", style="cyan", width=20)
        orders_table.add_column("Symbol", style="white", width=8)
        orders_table.add_column("Side", style="white", width=6)
        orders_table.add_column("Type", style="white", width=10)
        orders_table.add_column("Qty", style="white", width=6, justify="right")
        orders_table.add_column("Price", style="white", width=10, justify="right")
        orders_table.add_column("Status", style="white", width=10)
        orders_table.add_column("Created", style="white", width=12)
        
        for order in orders:
            order_id = order.get('order_id', 'N/A')
            symbol = order.get('stock_symbol', 'N/A')
            side = order.get('order_side', 'N/A')
            order_type = order.get('order_types', 'N/A')
            quantity = order.get('quantity', 0)
            price = order.get('price', 0)
            
            # Color coding for side
            side_color = "green" if side == 'BUY' else "red"
            
            # Format created datetime
            created_dt = order.get('order_datetime')
            if created_dt:
                if isinstance(created_dt, str):
                    created_str = created_dt[:10]  # Take first 10 chars (date part)
                else:
                    created_str = created_dt.strftime("%Y-%m-%d")
            else:
                created_str = 'N/A'
            
            orders_table.add_row(
                order_id,
                symbol,
                f"[{side_color}]{side}[/{side_color}]",
                order_type,
                str(quantity),
                f"₹{price:,.2f}",
                "[green]Executed[/green]",
                created_str
            )
        
        self.console.print()
        self.console.print(orders_table)
        self.console.print()
    
    def view_transactions(self, transactions: List[Dict[str, Any]]) -> None:
        """
        Display transactions in beautiful table format
        
        Args:
            transactions: List of transaction dictionaries
        """
        if not transactions:
            empty_panel = Panel(
                "No transactions found",
                title="💳 Transactions",
                border_style="yellow",
                padding=(1, 2)
            )
            self.console.print(empty_panel)
            return
        
        transactions_table = Table(
            title="💳 Transaction History",
            show_header=True,
            header_style="bold green",
            box=box.HEAVY_HEAD,
            title_style="bold cyan"
        )
        
        transactions_table.add_column("Transaction ID", style="cyan", width=20)
        transactions_table.add_column("Type", style="white", width=10)
        transactions_table.add_column("Amount", style="white", width=12, justify="right")
        transactions_table.add_column("Balance", style="white", width=12, justify="right")
        transactions_table.add_column("Status", style="white", width=10)
        transactions_table.add_column("Note", style="white", width=25)
        transactions_table.add_column("Date", style="white", width=12)
        
        for txn in transactions:
            txn_id = txn.get('transaction_id', 'N/A')
            txn_type = txn.get('transaction_type', 'N/A')
            amount = txn.get('amount', 0)
            balance = txn.get('balance_after', 0)
            status = txn.get('status', 'N/A')
            note = txn.get('note', 'N/A')[:23] + '...' if len(txn.get('note', '')) > 25 else txn.get('note', 'N/A')
            
            # Color coding for transaction type
            type_color = "green" if txn_type == 'DEPOSIT' else "red" if txn_type == 'WITHDRAWAL' else "blue"
            amount_color = "green" if amount > 0 else "red" if amount < 0 else "yellow"
            
            # Format date
            created_dt = txn.get('created_datetime')
            if created_dt:
                if isinstance(created_dt, str):
                    date_str = created_dt[:10]
                else:
                    date_str = created_dt.strftime("%Y-%m-%d")
            else:
                date_str = 'N/A'
            
            transactions_table.add_row(
                txn_id,
                f"[{type_color}]{txn_type}[/{type_color}]",
                f"[{amount_color}]₹{amount:,.2f}[/{amount_color}]",
                f"₹{balance:,.2f}",
                "[green]Completed[/green]" if status == 'SUCCESS' else f"[yellow]{status}[/yellow]",
                note,
                date_str
            )
        
        self.console.print()
        self.console.print(transactions_table)
        self.console.print()
    
    def view_portfolio_summary(self, account_data: Dict[str, Any], positions_data: Dict[str, Any]) -> None:
        """
        Display comprehensive portfolio summary
        
        Args:
            account_data: Account information
            positions_data: Positions and overview data
        """
        overview = positions_data.get('overview', {})
        
        # Create summary panels
        account_info = [
            f"👤 {account_data.get('full_name', 'N/A')}",
            f"📧 {account_data.get('email_id', 'N/A')}",
            f"🆔 {account_data.get('account_id', 'N/A')}"
        ]
        
        financial_info = [
            f"💰 Balance: ₹{account_data.get('balance', 0):,.2f}",
            f"💸 Invested: ₹{overview.get('invested_amount', 0):,.2f}",
        ]
        
        total_pnl = overview.get('total_pnl', 0)
        pnl_color = "green" if total_pnl > 0 else "red" if total_pnl < 0 else "yellow"
        financial_info.append(f"📈 Total P&L: [{pnl_color}]₹{total_pnl:,.2f}[/{pnl_color}]")
        
        positions_info = [
            f"📊 Total: {overview.get('total_positions', 0)}",
            f"🟢 Open: {overview.get('open_positions', 0)}",
            f"🔴 Closed: {overview.get('closed_positions', 0)}",
            f"✅ Profit: {overview.get('positive_pnl_count', 0)}",
            f"❌ Loss: {overview.get('negative_pnl_count', 0)}"
        ]
        
        # Create panels
        account_panel = Panel(
            "\n".join(account_info),
            title="👤 Account Info",
            border_style="blue",
            padding=(1, 2)
        )
        
        financial_panel = Panel(
            "\n".join(financial_info),
            title="💰 Financial Summary",
            border_style="green",
            padding=(1, 2)
        )
        
        positions_panel = Panel(
            "\n".join(positions_info),
            title="📊 Positions Summary",
            border_style="yellow",
            padding=(1, 2)
        )
        
        # Display in columns
        self.console.print()
        self.console.print(
            Panel(
                Columns([account_panel, financial_panel, positions_panel], equal=True, expand=True),
                title="📈 Trade Buddy Portfolio Dashboard",
                border_style="magenta",
                padding=(0, 1)
            )
        )
        self.console.print()
    
    def print_success(self, message: str) -> None:
        """Print success message with formatting"""
        self.console.print(f"✅ [green]{message}[/green]")
    
    def print_error(self, message: str) -> None:
        """Print error message with formatting"""
        self.console.print(f"❌ [red]{message}[/red]")
    
    def print_info(self, message: str) -> None:
        """Print info message with formatting"""
        self.console.print(f"ℹ️  [blue]{message}[/blue]")
    
    def print_warning(self, message: str) -> None:
        """Print warning message with formatting"""
        self.console.print(f"⚠️  [yellow]{message}[/yellow]")


# Global view instance for easy access
view = TradeBuddyView()