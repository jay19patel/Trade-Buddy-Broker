class TradeCalculator:

    # ==============================================================
    @staticmethod
    def calculate_quantity(capital: float, mark_price: float, contract_value: float, leverage: int, side: str = "buy") -> dict:
        """
        Calculate integer quantity using fixed 30% of capital and half leverage.
        - 30% of capital is used for each trade.
        - Leverage is automatically halved.
        - Quantity rounded down to nearest integer (no fractional contracts).
        side = "buy" or "sell"
        """
        side = side.lower()
        trade_percent = 30  # fixed

        # ✅ Half leverage logic
        effective_leverage = leverage / 2

        used_capital = capital * (trade_percent / 100)

        # Raw quantity (can be fractional)
        raw_quantity = (used_capital * effective_leverage) / (mark_price * contract_value)

        # Integer quantity (whole number of contracts)
        quantity = int(raw_quantity)

        return {
            "used_capital": round(used_capital, 2),
            "quantity": quantity,
            "lot_size": contract_value,
            "entry_price": round(mark_price, 4),
        }

    # ==============================================================
    @staticmethod
    def calculate_stop_target(current_price: float, side: str, liquidation_price: float) -> dict:
        """
        Calculate stoploss and target for given side and leverage.
        Also include liquidation and warning price.
        side = "buy" or "sell"
        """
        side = side.lower()

        risk_ratio = 0.02   # 2% stop
        reward_ratio = 0.04 # 4% target

        if side == "buy":
            stop_loss = current_price * (1 - risk_ratio)
            target = current_price * (1 + reward_ratio)
            # liquidation price niche hota hai → warning 10% pehle (upar)
            liquidation_warning_price = liquidation_price + (current_price - liquidation_price) * 0.1
        else:  # sell
            stop_loss = current_price * (1 + risk_ratio)
            target = current_price * (1 - reward_ratio)
            # liquidation price upar hota hai → warning 10% pehle (niche)
            liquidation_warning_price = liquidation_price - (liquidation_price - current_price) * 0.1


        return {
            "side": side,
            "entry_price": round(current_price, 4),
            "stop_loss": round(stop_loss, 4),
            "target": round(target, 4),
            "liquidation_price": round(liquidation_price, 4),
            "liquidation_warning_price": round(liquidation_warning_price, 4),
        }
