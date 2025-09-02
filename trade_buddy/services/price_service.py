"""
Live price data service
"""

import requests
from typing import List, Dict, Any, Optional
from requests.exceptions import RequestException
from ..core.exceptions import TradeBuddyException


class PriceService:
    """Service for fetching live stock price data"""
    
    def __init__(self):
        self.base_url = "https://groww.in/v1/api"
        self.timeout = 10
    
    def search_symbols(self, query: str) -> List[Dict[str, Any]]:
        """Search for stock/option symbols"""
        try:
            if not query or len(query.strip()) < 2:
                raise TradeBuddyException("Search query must be at least 2 characters")
            
            url = f"{self.base_url}/search/v3/query/global/st_p_query"
            params = {
                "page": 0, 
                "query": query.strip(), 
                "size": 10, 
                "web": "true"
            }
            
            response = requests.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            
            data = response.json()
            return data.get("data", {}).get("content", [])
            
        except RequestException as e:
            raise TradeBuddyException(f"Failed to search symbols: {str(e)}")
        except Exception as e:
            raise TradeBuddyException(f"Symbol search error: {str(e)}")
    
    def get_stock_price(self, symbol_id: str, symbol_type: str = "Stocks") -> Optional[Dict[str, Any]]:
        """Get live price data for a symbol"""
        try:
            if not symbol_id:
                raise TradeBuddyException("Symbol ID cannot be empty")
            
            if symbol_type == "Stocks":
                return self._fetch_stock_data(symbol_id)
            elif symbol_type == "Option":
                return self._fetch_option_data(symbol_id)
            else:
                raise TradeBuddyException("Invalid symbol type. Use 'Stocks' or 'Option'")
                
        except TradeBuddyException:
            raise
        except Exception as e:
            raise TradeBuddyException(f"Failed to fetch price data: {str(e)}")
    
    def _fetch_stock_data(self, symbol_id: str) -> Optional[Dict[str, Any]]:
        """Fetch stock price data"""
        try:
            url = f"{self.base_url}/stocks_data/v1/accord_points/exchange/NSE/segment/CASH/latest_prices_ohlc/{symbol_id}"
            params = {"page": 0, "size": 10}
            
            response = requests.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            
            data = response.json()
            
            return {
                "name": data.get("symbol"),
                "id": symbol_id,
                "type": "Stocks",
                "ltp": data.get("ltp"),
                "open": data.get("open", data.get("ltp")),
                "high": data.get("high"),
                "low": data.get("low"),
                "volume": data.get("volume"),
                "close": data.get("close"),
                "change": data.get("dayChange"),
                "changePercent": data.get("dayChangePerc")
            }
            
        except RequestException:
            return None
        except Exception:
            return None
    
    def _fetch_option_data(self, contract_id: str) -> Optional[Dict[str, Any]]:
        """Fetch option price data"""
        try:
            url = f"{self.base_url}/stocks_fo_data/v1/derivatives/nifty/contract?groww_contract_id={contract_id}"
            
            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            data = response.json()
            live_price = data.get("livePrice", {})
            
            return {
                "name": contract_id,
                "id": contract_id,
                "type": "Option",
                "ltp": live_price.get("ltp"),
                "open": live_price.get("open"),
                "high": live_price.get("high"),
                "low": live_price.get("low"),
                "close": live_price.get("close"),
                "volume": live_price.get("volume"),
                "change": live_price.get("dayChange"),
                "changePercent": live_price.get("dayChangePerc")
            }
            
        except RequestException:
            return None
        except Exception:
            return None
    
    def get_multiple_prices(self, symbols: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """Get price data for multiple symbols"""
        if not symbols:
            return []
        
        results = []
        for symbol in symbols:
            try:
                symbol_id = symbol.get("id")
                symbol_type = symbol.get("type", "Stocks")
                
                if symbol_id:
                    price_data = self.get_stock_price(symbol_id, symbol_type)
                    if price_data:
                        results.append(price_data)
                        
            except Exception:
                continue  # Skip failed symbols
        
        return results