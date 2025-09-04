"""
Lightweight in-memory Position service with stoploss/target updates.
"""

from datetime import datetime
from typing import Dict, List, Optional

from trade_buddy.entities.models import Account
from trade_buddy.utils.security import SecurityManager


class PositionService:
    """Simple in-memory positions for demo/testing.
    Structure:
      position = {
        'position_id', 'account_id', 'symbol_id', 'side', 'quantity',
        'avg_price', 'status', 'opened_at', 'closed_at', 'exit_price',
        'pnl', 'stoploss', 'target'
      }
    """

    _positions: Dict[str, Dict] = {}
    _by_account: Dict[str, List[str]] = {}

    def __init__(self):
        self.security = SecurityManager()

    def open_position(
        self,
        account: Account,
        symbol_id: str,
        quantity: int,
        price: float,
        side: str,
        stoploss: Optional[float] = None,
        target: Optional[float] = None,
    ) -> Dict:
        position_id = self.security.generate_unique_id("POS")
        pos = {
            "position_id": position_id,
            "account_id": account.account_id,
            "symbol_id": symbol_id,
            "quantity": int(quantity),
            "avg_price": float(price),
            "side": side.upper(),
            "status": "OPEN",
            "opened_at": datetime.now().isoformat(),
            "closed_at": None,
            "exit_price": None,
            "pnl": None,
            "stoploss": stoploss,
            "target": target,
        }
        self._positions[position_id] = pos
        self._by_account.setdefault(account.account_id, []).append(position_id)
        return pos

    def update_levels(
        self,
        account: Account,
        position_id: str,
        stoploss: Optional[float] = None,
        target: Optional[float] = None,
    ) -> Dict:
        pos = self._positions.get(position_id)
        if not pos or pos["account_id"] != account.account_id:
            raise ValueError("Position not found")
        if stoploss is not None:
            pos["stoploss"] = float(stoploss)
        if target is not None:
            pos["target"] = float(target)
        return pos

    def exit_position(self, account: Account, position_id: str, exit_price: float) -> Dict:
        pos = self._positions.get(position_id)
        if not pos or pos["account_id"] != account.account_id:
            raise ValueError("Position not found")
        if pos["status"] != "OPEN":
            return pos
        pos["status"] = "CLOSED"
        pos["closed_at"] = datetime.now().isoformat()
        pos["exit_price"] = float(exit_price)
        multiplier = 1 if pos["side"] == "BUY" else -1
        pos["pnl"] = round((pos["exit_price"] - pos["avg_price"]) * pos["quantity"] * multiplier, 2)
        return pos

    def get_open_positions(self, account_id: str) -> List[Dict]:
        ids = self._by_account.get(account_id, [])
        return [self._positions[i] for i in ids if self._positions[i]["status"] == "OPEN"]

    def get_position_history(self, account_id: str) -> List[Dict]:
        ids = self._by_account.get(account_id, [])
        return [self._positions[i] for i in ids if self._positions[i]["status"] == "CLOSED"]


