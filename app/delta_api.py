from delta_rest_client import DeltaRestClient
from delta_rest_client.delta_rest_client import OrderType as DeltaOrderType
from typing import Dict, Any, Optional, List


class DeltaAPI:
    """
    Delta Exchange API Wrapper - Simple and Fast

    This class wraps the Delta Rest Client with simple parameter passing
    for better performance and reduced execution time.
    """

    def __init__(self, base_url: str, api_key: str, api_secret: str):
        """
        Initialize Delta API client

        Args:
            base_url: Base URL for Delta Exchange API
                - Production-India: https://api.india.delta.exchange
                - Testnet-India: https://cdn-ind.testnet.deltaex.org
                - Production-Global: https://api.delta.exchange
                - Testnet-Global: https://testnet-api.delta.exchange
            api_key: Your Delta Exchange API key
            api_secret: Your Delta Exchange API secret
        """
        self.client = DeltaRestClient(
            base_url=base_url,
            api_key=api_key,
            api_secret=api_secret
        )

    def _convert_order_type(self, order_type: str) -> DeltaOrderType:
        """Convert string order type to Delta's OrderType enum"""
        if order_type.lower() == "market":
            return DeltaOrderType.MARKET
        elif order_type.lower() == "limit":
            return DeltaOrderType.LIMIT
        else:
            raise ValueError(f"Unsupported order type: {order_type}")

    # ==================== Market Data Methods ====================

    def get_assets(self) -> Dict[str, Any]:
        """
        Get list of assets supported on Delta Exchange

        Returns:
            Response containing list of assets
        """
        return self.client.get_assets()

    def get_product(self, product_id: int) -> Dict[str, Any]:
        """
        Get product detail of a specific product

        Args:
            product_id: ID of the product

        Returns:
            Product details including settling_asset and other info
        """
        return self.client.get_product(product_id)

    def get_ticker(self, symbol: str) -> Dict[str, Any]:
        """
        Get 24hr ticker data for a symbol

        Args:
            symbol: Product symbol

        Returns:
            Ticker data response
        """
        return self.client.get_ticker(symbol)

    def get_l2_orderbook(self, product_id: int) -> Dict[str, Any]:
        """
        Get level-2 orderbook of the product

        Args:
            product_id: ID of the product

        Returns:
            L2 orderbook data
        """
        return self.client.get_l2_orderbook(product_id)

    # ==================== Order Methods ====================

    def get_live_orders(self) -> Dict[str, Any]:
        """
        Get all open orders (requires authorization)

        Returns:
            List of open orders
        """
        return self.client.get_live_orders()

    def place_order(self, product_id: int, size: int, side: str, order_type: str, 
                   limit_price: Optional[str] = None, reduce_only: bool = False) -> Dict[str, Any]:
        """
        Place a new market or limit order

        Args:
            product_id: ID of the product
            size: Order size
            side: 'buy' or 'sell'
            order_type: 'limit' or 'market'
            limit_price: Order price (required for limit orders)
            reduce_only: Reduce only order

        Returns:
            Order response with order details
        """
        # For regular orders, we need to use place_stop_order but without stop-specific parameters
        kwargs = {
            'product_id': product_id,
            'size': size,
            'side': side.lower(),
            'order_type': self._convert_order_type(order_type),
        }
        
        if limit_price:
            kwargs['limit_price'] = limit_price
            
        if reduce_only:
            kwargs['reduce_only'] = str(reduce_only).lower()
            
        # The API requires stop_price even for regular orders, so we provide a dummy value
        # that won't trigger (very far from current price)
        if side.lower() == 'buy':
            kwargs['stop_price'] = '1000000'  # Very high price that won't trigger
        else:
            kwargs['stop_price'] = '1'  # Very low price that won't trigger
            
        return self.client.place_stop_order(**kwargs)

    def place_stop_order(self, product_id: int, size: float, side: str, order_type: str,
                        stop_price: Optional[str] = None, trail_amount: Optional[str] = None,
                        limit_price: Optional[str] = None, is_trailing_stop_loss: bool = False) -> Dict[str, Any]:
        """
        Place a stop loss or trailing stop loss order

        Args:
            product_id: ID of the product
            size: Order size
            side: 'buy' or 'sell'
            order_type: 'limit' or 'market'
            stop_price: Price at which order will be triggered (for stop loss)
            trail_amount: Trail price (for trailing stop loss)
            limit_price: Order price (ignored if market order)
            is_trailing_stop_loss: True for trailing stop loss, false for regular stop loss

        Returns:
            Order response with order details
        """
        kwargs = {
            'product_id': product_id,
            'size': size,
            'side': side.lower(),
            'order_type': self._convert_order_type(order_type),
        }

        if limit_price:
            kwargs['limit_price'] = limit_price

        if is_trailing_stop_loss:
            kwargs['trail_amount'] = trail_amount
            kwargs['isTrailingStopLoss'] = True
        else:
            kwargs['stop_price'] = stop_price

        return self.client.place_stop_order(**kwargs)

    def cancel_order(self, product_id: int, order_id: int) -> Dict[str, Any]:
        """
        Cancel an open order

        Args:
            product_id: ID of the product
            order_id: Order ID to cancel

        Returns:
            Cancellation response
        """
        return self.client.cancel_order(product_id, order_id)

    def batch_create_orders(self, product_id: int, orders: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Create multiple limit orders (max 5)

        Args:
            product_id: ID of the product
            orders: List of order dictionaries with keys: size, side, limit_price, order_type

        Returns:
            Batch create response
        """
        formatted_orders = [
            {
                'size': order['size'],
                'side': order['side'].lower(),
                'limit_price': order['limit_price'],
                'order_type': self._convert_order_type(order['order_type'])
            }
            for order in orders
        ]
        return self.client.batch_create(product_id, formatted_orders)

    def batch_cancel_orders(self, product_id: int, order_ids: List[int]) -> Dict[str, Any]:
        """
        Cancel multiple open orders (max 5)

        Args:
            product_id: ID of the product
            order_ids: List of order IDs to cancel

        Returns:
            Batch cancel response
        """
        orders = [{'order_id': order_id} for order_id in order_ids]
        return self.client.batch_cancel(product_id, orders)

    def get_order_history(self, query: Dict[str, Any], page_size: int = 100, after: Optional[str] = None) -> Dict[str, Any]:
        """
        Get order history with pagination

        Args:
            query: Query filters (e.g., {'product_id': 27})
            page_size: Number of records per page (max 1000)
            after: Cursor for next page pagination

        Returns:
            Order history with pagination metadata
        """
        kwargs = {'page_size': page_size}
        if after:
            kwargs['after'] = after
        return self.client.order_history(query, **kwargs)

    def get_fills(self, query: Dict[str, Any], page_size: int = 100, after: Optional[str] = None) -> Dict[str, Any]:
        """
        Get fill history of your orders with pagination

        Args:
            query: Query filters (e.g., {'contract_types': 'futures,interest_rate_swaps'})
            page_size: Number of records per page (max 1000)
            after: Cursor for next page pagination

        Returns:
            Fills history with pagination metadata
        """
        kwargs = {'page_size': page_size}
        if after:
            kwargs['after'] = after
        return self.client.fills(query, **kwargs)

    # ==================== Position Methods ====================

    def get_position(self, product_id: int) -> Dict[str, Any]:
        """
        Get current open position for a product

        Args:
            product_id: ID of the product

        Returns:
            Position details
        """
        return self.client.get_position(product_id)

    def change_position_margin(self, product_id: int, margin: str) -> Dict[str, Any]:
        """
        Change margin for an open position by adding or removing margin

        Args:
            product_id: ID of the product
            margin: New margin amount

        Returns:
            Response with updated position
        """
        return self.client.change_position_margin(product_id, margin)

    def set_leverage(self, product_id: int, leverage: str) -> Dict[str, Any]:
        """
        Change leverage for new orders

        Args:
            product_id: ID of the product
            leverage: Leverage value (e.g., '10', '25', '100')

        Returns:
            Response confirming leverage change
        """
        return self.client.set_leverage(product_id, leverage)

    # ==================== Wallet Methods ====================

    def get_balances(self, asset_id: int) -> Dict[str, Any]:
        """
        Get user's wallet balance for an asset

        Args:
            asset_id: ID of the asset

        Returns:
            Balance information
        """
        return self.client.get_balances(asset_id)