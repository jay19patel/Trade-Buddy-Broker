# Trade Buddy SDK

A simple and powerful Python SDK for paper trading with broker-like functionality. Trade Buddy SDK allows you to simulate trading operations without real money, perfect for learning, backtesting, and strategy development.

## Features

- 🔐 **User Authentication**: Registration, login, and email verification
- 📈 **Order Management**: Create, modify, and close trading positions
- 💰 **Portfolio Tracking**: Real-time balance and position tracking
- 📊 **Live Price Data**: Fetch real-time stock and option prices
- 💳 **Transaction Management**: Deposit and withdraw virtual funds
- 🎯 **Stop-Loss & Target**: Automated risk management
- 📧 **Email Notifications**: Account verification and notifications
- 🎫 **Support System**: Built-in ticketing system

## Installation

```bash
pip install trade-buddy-sdk
```

## Quick Start

```python
import asyncio
from trade_buddy_sdk import TradeBuddy, Registration, Login, CreateNewOrder
from trade_buddy_sdk.models import OrderSide, StockType, CreateBy

# Initialize the broker
broker = TradeBuddy()

async def main():
    # Register a new user
    registration_data = Registration(
        email_id="trader@example.com",
        password="secure123",
        full_name="John Trader",
        max_trad_per_day=10,
        base_stoploss=5.0,
        base_target=10.0,
        description="Active day trader"
    )
    
    response = await broker.registration(registration_data)
    print(f"Registration: {response.message}")
    
    # Login
    login_data = Login(
        user_id="trader@example.com",
        password="secure123"
    )
    
    login_response = await broker.login(login_data)
    print(f"Login: {login_response.message}")
    
    # Add funds to account
    from trade_buddy_sdk.schemas import TransactionRequest
    deposit = TransactionRequest(
        transaction_type="DEPOSIT",
        amount=10000.0,
        note="Initial deposit"
    )
    
    await broker.create_transaction(deposit)
    print("Funds added to account")
    
    # Search for a stock
    search_results = broker.search_symbols("RELIANCE")
    print(f"Search results: {len(search_results)} symbols found")
    
    # Get live price
    price_data = broker.get_live_price("RELIANCE", "Stocks")
    if price_data:
        print(f"RELIANCE LTP: ₹{price_data['ltp']}")
    
    # Create a new order
    order_data = CreateNewOrder(
        stock_symbol="RELIANCE",
        order_side=OrderSide.BUY,
        stock_type=StockType.STOCK,
        price=2500.0,
        stoploss_price=2400.0,
        target_price=2600.0,
        quantity=10,
        created_by=CreateBy.MANUAL
    )
    
    order_response = await broker.create_new_order(order_data)
    print(f"Order created: {order_response.message}")
    
    # Get positions
    positions = await broker.get_positions()
    print(f"Active positions: {positions['overview']['open_positions']}")
    print(f"Account balance: ₹{positions['overview']['balance']}")

# Run the example
asyncio.run(main())
```

## Core Classes

### TradeBuddy

Main broker class providing all trading functionality:

```python
from trade_buddy_sdk import TradeBuddy

broker = TradeBuddy(secret_key="your-secret-key")  # Optional custom secret
```

### Key Methods

#### Authentication
```python
# Register new user
await broker.registration(registration_data)

# Login user
await broker.login(login_data)

# Get account details
account = await broker.get_account_details()

# Logout
await broker.logout()
```

#### Order Management
```python
# Create new position
await broker.create_new_order(order_data)

# Add stop-loss
await broker.create_stoploss_order(stoploss_data)

# Update quantity
await broker.update_quantity_order(update_data)

# Exit position
await broker.create_exit_order(exit_data)
```

#### Portfolio & Data
```python
# Get positions
positions = await broker.get_positions()

# Get all completed positions
history = await broker.get_all_positions()

# Search symbols
results = broker.search_symbols("NIFTY")

# Get live price
price = broker.get_live_price("RELIANCE", "Stocks")
```

#### Account Management
```python
# Add/withdraw funds
await broker.create_transaction(transaction_data)

# Send support ticket
await broker.send_support_ticket(ticket_data)

# Verify email
await broker.verify_email(verification_token)
```

## Data Models

### Order Sides
- `OrderSide.BUY`: Buy order
- `OrderSide.SELL`: Sell order

### Stock Types
- `StockType.STOCK`: Equity stocks
- `StockType.OPTION`: Options contracts

### Order Types
- `OrderTypes.NewOrder`: New position
- `OrderTypes.StopLossOrder`: Stop-loss order
- `OrderTypes.UpdateQtyOrder`: Quantity update
- `OrderTypes.ExitOrder`: Position exit

### Position Status
- `PositionStatus.PENDING`: Active position
- `PositionStatus.COMPLETED`: Closed position

## Schemas

All input data uses Pydantic schemas for validation:

### Registration
```python
from trade_buddy_sdk.schemas import Registration

registration_data = Registration(
    email_id="trader@example.com",
    password="secure123",
    full_name="John Trader",
    max_trad_per_day=5,
    base_stoploss=5.0,
    base_target=10.0,
    trailing_status=True,
    trailing_stoploss=10.0,
    trailing_target=10.0,
    description="Paper trader"
)
```

### Order Creation
```python
from trade_buddy_sdk.schemas import CreateNewOrder
from trade_buddy_sdk.models import OrderSide, StockType, CreateBy

order_data = CreateNewOrder(
    stock_symbol="RELIANCE",
    order_side=OrderSide.BUY,
    stock_type=StockType.STOCK,
    price=2500.0,
    stoploss_price=2400.0,
    target_price=2600.0,
    quantity=10,
    created_by=CreateBy.MANUAL
)
```

## Error Handling

The SDK uses `TBException` for all errors:

```python
from trade_buddy_sdk.models import TBException

try:
    await broker.create_new_order(order_data)
except TBException as e:
    print(f"Error: {e.message}")
    print(f"Resolution: {e.resolution}")
    print(f"Status Code: {e.status_code}")
```

## Response Format

All operations return `TBResponse` objects:

```python
response = await broker.login(login_data)
print(response.message)      # Success message
print(response.payload)      # Response data
print(response.success)      # Boolean success flag
print(response.to_dict())    # Convert to dictionary
```

## Live Price Data

Get real-time market data:

```python
# Search for symbols
symbols = broker.search_symbols("NIFTY")

# Get single price
price = broker.get_live_price("RELIANCE", "Stocks")

# Get multiple prices
symbols_list = [
    {"id": "RELIANCE", "type": "Stocks"},
    {"id": "TCS", "type": "Stocks"}
]
prices = broker.get_multiple_live_prices(symbols_list)
```

## Account Management

### Transactions
```python
from trade_buddy_sdk.schemas import TransactionRequest

# Deposit funds
deposit = TransactionRequest(
    transaction_type="DEPOSIT",
    amount=10000.0,
    note="Initial funding"
)
await broker.create_transaction(deposit)

# Withdraw funds
withdraw = TransactionRequest(
    transaction_type="WITHDRAW", 
    amount=500.0,
    note="Profit booking"
)
await broker.create_transaction(withdraw)
```

### Support Tickets
```python
from trade_buddy_sdk.schemas import TicketBase

ticket = TicketBase(
    email="trader@example.com",
    title="Need help with orders",
    message="I'm having trouble creating stop-loss orders"
)
await broker.send_support_ticket(ticket)
```

## Position Management

### Position Overview
```python
positions = await broker.get_positions()

overview = positions['overview']
print(f"Open Positions: {overview['open_positions']}")
print(f"Closed Positions: {overview['closed_positions']}")
print(f"Total P&L: ₹{overview['pnl_total']}")
print(f"Today's P&L: ₹{overview['pnl_todays']}")
print(f"Account Balance: ₹{overview['balance']}")
print(f"Invested Amount: ₹{overview['invested_amount']}")

# Individual positions
for position in positions['positions']:
    print(f"Symbol: {position['stock_symbol']}")
    print(f"Quantity: {position['buy_quantity'] - position['sell_quantity']}")
    print(f"P&L: ₹{position['pnl_total']}")
```

## Advanced Usage

### Custom Configuration
```python
# Initialize with custom secret key
broker = TradeBuddy(secret_key="my-custom-secret-2024")

# Access internal services
security_manager = broker.security
database = broker.database
email_service = broker.email_service
price_service = broker.live_price
```

### Demo Account
The SDK comes with a pre-configured demo account:
- **Email**: demo@tradebuddy.com
- **Password**: demo123
- **Balance**: ₹100,000

## Requirements

- Python 3.8+
- pydantic>=2.0.0
- bcrypt>=4.0.0
- PyJWT>=2.8.0
- requests>=2.28.0
- email-validator>=2.0.0

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Email: support@tradebuddy.com
- GitHub Issues: [Create an issue](https://github.com/tradebuddy/trade-buddy-sdk/issues)

---

**Disclaimer**: This SDK is for educational and simulation purposes only. It does not involve real money or actual trading. Always consult with financial advisors for real investment decisions.