from fastapi import Depends,HTTPException
from app.Database.base import get_db, AsyncSession
from app.Models.models import Account
from sqlalchemy import select
from app.Core.security import AccessTokenBearer

async def get_account_from_token(request: dict = Depends(AccessTokenBearer()),db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(Account).where(Account.account_id == request["AccountId"]))
        account = result.scalars().first()
        if not account:
            raise HTTPException(detail="Not Authenticated !",status_code=404)
        return account
    except:
        raise HTTPException(detail="Something went to wrong in Authentication !",status_code=404)
    
import time

def generate_unique_id(input_string: str) -> str:
    timestamp = time.time() + 19
    timestamp_str = str(timestamp).replace('.', '')  # Remove the dot from the timestamp string
    unique_string = f"TB-{timestamp_str}-{input_string.upper()}"
    return unique_string

import requests
from requests.exceptions import RequestException
def fetch_search_data(query):
    url = "https://groww.in/v1/api/search/v3/query/global/st_p_query"
    params = {"page": 0, "query": query, "size": 5, "web": "true"} 
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()  # Raise an error for bad responses (4xx or 5xx)
        data = response.json()
        return data.get("data", {}).get("content", [])
    
    except (RequestException, ValueError) as e:
        print(f"Error fetching data: {e}")
        return []  # Return an empty list in case of an error
    
def fetch_stock_data(search_id,type_of_symbol):
    if type_of_symbol == "Stocks":
        url = f"https://groww.in/v1/api/stocks_data/v1/accord_points/exchange/NSE/segment/CASH/latest_prices_ohlc/{search_id}"
        params = {"page": 0, "size": 10}
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()  # Raise an error for bad responses (4xx or 5xx)
            data = response.json()
            return {"name": data.get("symbol") ,
                    "id": None,
                    "type":"Stocks",
                    "ltp": data.get("ltp"),
                    'open': data.get("ltp"),
                    'high': data.get("high"),
                    'low': data.get("low"),
                    'volume' : data.get("volume"),
                    'close': data.get("close"),
                    "change":data.get("dayChange"),
                    'changePercent':data.get("dayChangePerc"),
                  }
        except (RequestException, ValueError) as e:
            print(f"Error fetching stock data: {e}")
            return None

    elif type_of_symbol == "Option" :
        url = f"https://groww.in/v1/api/stocks_fo_data/v1/derivatives/nifty/contract?groww_contract_id={search_id}"
        try:
          response = requests.get(url, timeout=10)
          response.raise_for_status()  # Raise an error for bad responses (4xx or 5xx)
          data = response.json()
          return { "name": data.get("contractDetails").get("displayName"),
                  "ltp": data.get("livePrice").get("ltp"),
                    'open': data.get("livePrice").get("open"),
                    'high': data.get("livePrice").get("high"),
                    'low': data.get("livePrice").get("low"),
                    'close': data.get("livePrice").get("close"),
                    'volume' : data.get("livePrice").get("volume"),
                   "change":data.get("livePrice").get("dayChange"),
                   "changePercent":data.get("livePrice").get("dayChangePerc"),
                  }
        except (RequestException, ValueError) as e:
          print(f"Error fetching stock data: {e}")
          return None
    else:
        return None