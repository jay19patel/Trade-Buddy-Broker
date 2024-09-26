from fastapi import APIRouter, Query, HTTPException
from typing import Optional
from app.Core.utility import fetch_search_data,fetch_stock_data
# Initialize the router
home_route = APIRouter()



@home_route.get("/search")
async def search_symbol(
    q: Optional[str] = Query(None, alias="q")
):
    try:
        result = fetch_search_data(q)
        return result
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@home_route.get("/find")
async def find_symbol(
    type_of_symbol: Optional[str] = Query(None, alias="type_of_symbol"),
    symbol_id: Optional[str] = Query(None, alias="symbol_id")
):
    try:
        result = fetch_stock_data(symbol_id,type_of_symbol)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

