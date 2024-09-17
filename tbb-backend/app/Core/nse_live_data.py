import aiohttp
import asyncio
import pandas as pd
from urllib.parse import urljoin
import json
from datetime import datetime,time
class TradeBuddyNSE:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36",
            "Referer": "https://www.nseindia.com/get-quotes/equity?symbol=SBIN",
            "X-Requested-With": "XMLHttpRequest",
        }
        self.base_url = "https://www.nseindia.com"
        self.ssl_verify = True
        self.session = aiohttp.ClientSession(headers=self.headers)

    async def close(self):
        await self.session.close()

    async def _initialize_session(self):
        url = urljoin(self.base_url, "/get-quotes/equity")
        async with self.session.get(url, ssl=self.ssl_verify) as response:
            if response.status == 200:
                print("Session Initialized Successfully")
            else:
                raise Exception(f"Failed to initialize session: {response.status} {response.text}")

    async def getNSEStockList(self, indexName):
        """Get list of stock with some basic information."""
        url = f"https://www.nseindia.com/api/equity-stockIndices?index={indexName}"
        async with self.session.get(url, ssl=self.ssl_verify) as response:
            if response.status == 200:
                data = await response.json()
                df = pd.DataFrame(data['data'][1:])
                df['isin'] = df['meta'].apply(lambda x: x.get('isin') if isinstance(x, dict) else None)
                df['industry'] = df['meta'].apply(lambda x: x.get('industry') if isinstance(x, dict) else None)
                df['companyName'] = df['meta'].apply(lambda x: x.get('companyName') if isinstance(x, dict) else None)
                return df.sort_values(by='pChange')
            else:
                raise Exception(f"Failed to fetch data: {response.status} {response.text}")

    async def getNSEIndexList(self):
        """Get list of index with some basic information."""
        url = f"https://www.nseindia.com/api/allIndices"
        async with self.session.get(url, ssl=self.ssl_verify) as response:
            if response.status == 200:
                data = await response.json()
                return pd.DataFrame(data['data'][1:])
            else:
                raise Exception(f"Failed to fetch data: {response.status} {response.text}")


async def fetch_stock_data(row, nse, all_stocks_df):
    index_name = row["indexSymbol"]
    try:
        stock_data = await nse.getNSEStockList(index_name)
        if stock_data is not None and not stock_data.empty:
            stock_data = stock_data[["symbol", "identifier", "series", "isin", "industry", "companyName", 
                                     "lastPrice", "change", "pChange", "totalTradedVolume", "totalTradedValue", 
                                     "yearHigh", "nearWKH", "nearWKL", "perChange365d", "perChange30d"]]
            all_stocks_df.append(stock_data)
    except Exception as e:
        # print(f"Error processing {index_name}: {e}")
        pass

async def fetch_live_nse_data_live_price():
    print("[ NSE Live Price Fetch Run]")
    nse = TradeBuddyNSE()
    await nse._initialize_session()

    index_list = await nse.getNSEIndexList()
    all_stocks_df = []

    tasks = [fetch_stock_data(row, nse, all_stocks_df) for _, row in index_list.iterrows()]
    await asyncio.gather(*tasks)

    # Convert the list of DataFrames to a single DataFrame
    all_stocks_df = pd.concat(all_stocks_df, ignore_index=True)

    filtered_df = all_stocks_df.drop_duplicates(subset=['symbol'], keep='first')

    index_list = index_list[["key", "index", "indexSymbol", "last", "variation", "percentChange", "yearHigh", 
                             "yearLow", "declines", "advances", "unchanged", "perChange365d", "perChange30d", 
                             "previousDay", "oneWeekAgo", "oneMonthAgo", "oneYearAgo"]]
    index_list["series"] = "INDEX"
    combined_df = pd.concat([filtered_df, index_list], ignore_index=True)
    combined_df = combined_df.where(pd.notnull(combined_df), None)

    # ----------------IF CSV------------------------
    combined_df.to_csv("app/Database/all_stock_index.csv", index=False)

    # ----------------IF JSON-----------------
    # save_into_json = {
    #     "data":combined_df.to_dict(orient="records"),
    #     "last_updated_time":datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # }

    # with open("app/Database/all_stock_index.json", "w") as f:
    #     json.dump(save_into_json, f, indent=4)
    
    await nse.close()

if __name__ == "__main__":
    pass
    # asyncio.run(fetch_live_nse_data_live_price())
