from decimal import Decimal, getcontext
from pydantic import BaseModel, Field, field_validator

# ✅ High precision for financial calculations
getcontext().prec = 28


# ✅ Input model (with trade side)
class TradeSetupInput(BaseModel):
    capital: float = Field(..., description="Total trading capital in USD")
    entry_price: float = Field(..., description="Current market price of the symbol (e.g., BTC/USD)")
    side: str = Field(..., description="Trade direction: 'buy' for long or 'sell' for short")

    @field_validator("side")
    def validate_side(cls, v):
        v = v.lower()
        if v not in {"buy", "sell"}:
            raise ValueError("side must be either 'buy' or 'sell'")
        return v


# ✅ Response model
class TradeManagerResponse(BaseModel):
    capital_usd: float
    entry_price: float
    side: str
    margin_used_usd: float
    position_size_usd: float
    quantity: float
    risk_amount_usd: float
    stop_distance_usd: float
    stop_loss_price: float
    target_price: float
    reward_ratio: float
    approx_liquidation_price: float
    liquidation_warning_price: float
    leverage: float


# ✅ Core calculation function
def calculate_trade_setup(data: TradeSetupInput) -> dict:
    """
    Calculate a complete trade setup including margin, quantity, stoploss, target,
    and liquidation warning, based on trade side (buy/sell).
    """

    # Default configuration
    DEFAULT_MARGIN_PERCENT = Decimal("30.0")
    DEFAULT_LEVERAGE = Decimal("50.0")
    DEFAULT_RISK_PERCENT = Decimal("1.5")
    DEFAULT_REWARD_RATIO = Decimal("2.0")
    DEFAULT_MAINTENANCE_MARGIN = Decimal("0.5")
    LIQUIDATION_WARNING_BUFFER = Decimal("0.10")  # 10% before liquidation

    # Convert to Decimal for precision
    capital = Decimal(str(data.capital))
    entry_price = Decimal(str(data.entry_price))
    side = data.side.lower()
    margin_percent = DEFAULT_MARGIN_PERCENT / Decimal("100")
    leverage = DEFAULT_LEVERAGE
    risk_percent = DEFAULT_RISK_PERCENT / Decimal("100")
    reward_ratio = DEFAULT_REWARD_RATIO
    maintenance_margin = DEFAULT_MAINTENANCE_MARGIN / Decimal("100")

    # Step 1: Margin & position size
    margin_used_usd = capital * margin_percent
    position_size_usd = margin_used_usd * leverage

    # Step 2: Quantity
    quantity = (position_size_usd / entry_price).quantize(Decimal("0.00000001"))

    # Step 3: Risk & target based on side
    risk_amount_usd = (capital * risk_percent).quantize(Decimal("0.01"))
    stop_distance_usd = (risk_amount_usd * entry_price / position_size_usd).quantize(Decimal("0.01"))

    if side == "buy":
        # Long trade: stop below, target above
        stop_loss_price = (entry_price - stop_distance_usd).quantize(Decimal("0.01"))
        target_price = (entry_price + stop_distance_usd * reward_ratio).quantize(Decimal("0.01"))
        liquidation_price = (
            entry_price * (Decimal("1") - (Decimal("1") / leverage) + maintenance_margin)
        ).quantize(Decimal("0.01"))
        liquidation_warning_price = (
            entry_price - ((entry_price - liquidation_price) * (Decimal("1") - LIQUIDATION_WARNING_BUFFER))
        ).quantize(Decimal("0.01"))

    else:
        # Short trade: stop above, target below
        stop_loss_price = (entry_price + stop_distance_usd).quantize(Decimal("0.01"))
        target_price = (entry_price - stop_distance_usd * reward_ratio).quantize(Decimal("0.01"))
        liquidation_price = (
            entry_price * (Decimal("1") + (Decimal("1") / leverage) - maintenance_margin)
        ).quantize(Decimal("0.01"))
        liquidation_warning_price = (
            entry_price + ((liquidation_price - entry_price) * (Decimal("1") - LIQUIDATION_WARNING_BUFFER))
        ).quantize(Decimal("0.01"))

    # ✅ Return as a plain dictionary
    return TradeManagerResponse(
        capital_usd=float(capital),
        entry_price=float(entry_price),
        side=side,
        margin_used_usd=float(margin_used_usd),
        position_size_usd=float(position_size_usd),
        quantity=float(quantity),
        risk_amount_usd=float(risk_amount_usd),
        stop_distance_usd=float(stop_distance_usd),
        stop_loss_price=float(stop_loss_price),
        target_price=float(target_price),
        reward_ratio=float(reward_ratio),
        approx_liquidation_price=float(liquidation_price),
        liquidation_warning_price=float(liquidation_warning_price),
        leverage=float(leverage),
    ).model_dump()


# ✅ Example run
if __name__ == "__main__":
    print("\n📈 BUY Example:")
    buy_data = TradeSetupInput(capital=100, entry_price=20000, side="buy")
    print(calculate_trade_setup(buy_data))

    print("\n📉 SELL Example:")
    sell_data = TradeSetupInput(capital=100, entry_price=20000, side="sell")
    print(calculate_trade_setup(sell_data))
