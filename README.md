# Trade Buddy Broker SDK 🚀

## Overview
**Trade Buddy Broker SDK** एक paper-trading SDK है जो clean layered architecture पर बना है. इसमें authentication, transactions, sessions, prices और basic positions (in-memory) शामिल हैं.

## 🎯 Features

- 👤 Registration, Login, Email Verify
- 🔐 JWT-based Sessions (create/validate/destroy)
- 💰 Account balance and details
- 💳 Transactions (Deposit/Withdraw)
- 📈 Live Prices and multiple prices
- 📦 Positions (open/update SL-TP/exit/list) — in-memory

## 🏗️ Architecture & Design

### Layers
```
📁 trade_buddy/
├── 📁 core/           # Core system components
│   ├── database.py    # Database connection & management (async-capable)
│   ├── response.py    # TBResponse unified structure
│   └── exceptions.py  # Custom exceptions
├── 📁 entities/       # Data models & schemas
│   ├── models.py      # SQLModel entities (types only for demo)
│   ├── schemas.py     # Pydantic validation schemas
│   └── response_schemas.py # API response schemas
├── 📁 repositories/   # Data access layer (in-memory for demo)
│   ├── account_repository.py
│   └── transaction_repository.py
├── 📁 services/       # Business logic layer (direct instantiation)
│   ├── auth_service.py
│   ├── transaction_service.py
│   ├── price_service.py
│   └── position_service.py
└── broker.py          # Main SDK interface
```

### Patterns
- Repository pattern (in-memory) for clear separation of data access and business logic
- Service layer for business rules
- Factory removed for simplicity; broker lazily creates service singletons per instance

## 🔧 Stack
- Python 3.13+
- SQLModel (entities only), in-memory repos for tests
- Pydantic for validation/serialization
- AsyncIO for broker/service APIs
- JWT via utils/security
- Requests for external price API

## 🚀 Quick Start
```bash
# Setup
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run end-to-end demo
python test_sdk.py
```

## 📚 Public Broker API
All methods return `TBResponse` with `message` and `data`.

### Auth
- `registration(data: dict)` → Create account
- `login(data: dict)` → Login + create session + JWT
- `verify_email(token: str)` → Mark verified
- `validate_token(token: str)` → Validate JWT
- `logout()` → Destroy session

### Account
- `get_account_details()` → Current user’s account details
- `get_current_balance()` → Current balance (float)

### Transactions
- `create_transaction({"transaction_type": "DEPOSIT|WITHDRAW", "amount": float, "note": str})`
  - Returns `{ transaction, new_balance }`

### Prices
- `search_symbols(query: str)` → list of symbols
- `get_live_price(symbol_id: str, symbol_type: str = "Stocks")` → single price
- `get_multiple_prices(symbols: List[{id, type}])` → multiple prices

### Positions (in-memory)
- `open_position(symbol_id, remaining_quantity, price, side, stoploss?, target?)`
- `update_position_levels(position_id, stoploss?, target?)`
- `exit_position(position_id, exit_price)`
- `get_open_positions()`
- `get_position_history()`

### Sessions / Maintenance
- `get_session_info()` → Details for current session
- `get_active_sessions_count()` → Count of active sessions
- `clear()` → Truncate DB tables and clear sessions

## 🧩 How the code works
- Broker lazily creates services (`AuthService`, `TransactionService`, `PriceService`, `PositionService`).
- Services encapsulate business logic; repositories store data (in-memory dicts shared across instances for accounts/transactions).
- Pricing uses `requests` and broker maps upstream fields into `PriceData` schema.
- Unified `TBResponse` keeps responses consistent across broker methods.

## 🧪 Test Flow
`test_sdk.py` covers the full flow: registration → login → account details → deposit → withdraw → prices → open/update/exit positions → session info → validate token → cleanup → logout.

## 🏭 Production hardening ideas
- Database
  - Replace in-memory repos with real DB repos (SQLAlchemy/SQLModel) and migrations
  - Use unique constraints and indexes; add read/write timeouts
- Security
  - Rotate JWT secret via env; support key rotation
  - Add brute-force protection/rate limits
- Reliability
  - Structured logging; standardized error payloads
  - Retries/timeouts and circuit breakers for price API
- Testing/Quality
  - Unit tests for services/repos + integration tests for broker
  - CI with linting (ruff/flake8), mypy, and test coverage
- Packaging
  - Semantic versioning and changelog
  - Optionally publish to private PyPI with pinned dependencies