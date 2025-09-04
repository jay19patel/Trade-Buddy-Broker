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