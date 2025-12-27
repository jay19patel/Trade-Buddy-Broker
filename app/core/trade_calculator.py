from app.core.config import config


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
        trade_percent = config.trade_percent
        risk_ratio = config.risk_ratio

        # -------------------------------------------------------------
        # 🛡️ Safe Leverage Calculation Logic
        # -------------------------------------------------------------
        # Goal: Ensure Liquidation Price is further away than Stop Loss
        # Liquidation Distance ≈ 1 / Leverage
        # Stop Loss Distance = risk_ratio
        # We need: Liquidation Dist > Stop Loss Dist
        # So: 1 / Leverage > risk_ratio  =>  Leverage < 1 / risk_ratio
        # We use a safety buffer factor (e.g., 0.8) to be safe.
        
        safety_buffer = 0.8
        max_safe_leverage = int(safety_buffer / risk_ratio)
        
        # Original logic: use half of provided leverage
        proposed_leverage = int(leverage / 2)
        
        # Take the minimum of proposed vs safe
        effective_leverage = min(proposed_leverage, max_safe_leverage)
        
        # Ensure at least 1x
        effective_leverage = max(1, effective_leverage)

        used_capital = capital * (trade_percent / 100)

        # Raw quantity (can be fractional) - using effective_leverage
        raw_quantity = (used_capital * effective_leverage) / (mark_price * contract_value)

        # Integer quantity (whole number of contracts)
        quantity = int(raw_quantity)

        return {
            "used_capital": used_capital,
            "quantity": quantity,
            "lot_size": contract_value,
            "entry_price": mark_price,
            "leverage": effective_leverage, # Return the actual leverage to be used
            "safe_leverage_limit": max_safe_leverage
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

        risk_ratio = config.risk_ratio
        reward_ratio = config.reward_ratio

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
            "entry_price": round(current_price, 8),
            "stop_loss": round(stop_loss, 8),
            "target": round(target, 8),
            "liquidation_price": round(liquidation_price, 8),
            "liquidation_warning_price": round(liquidation_warning_price, 8),
        }
