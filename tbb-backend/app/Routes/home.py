from fastapi import APIRouter, Query, HTTPException
from typing import Optional
import pandas as pd
import numpy as np

# Initialize the router
home_route = APIRouter()

@home_route.get("/symbol")
async def search_symbol(
    q: Optional[str] = Query(None, alias="q")
):
    try:
        df = pd.read_csv("app/Database/all_stock_index.csv")
        columns = ["symbol", "isin", "industry", "companyName","key","index","indexSymbol"]
        mask = df[columns].apply(lambda row: row.astype(str).str.contains(q, case=False).any(), axis=1)
        df_filtered = df[mask]
        df_filtered.replace([np.nan, np.inf, -np.inf], None, inplace=True)
        return df_filtered.reset_index(drop=True).to_dict(orient='records')
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
