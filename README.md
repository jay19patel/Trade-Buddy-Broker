

reduce_only=True 
Yeh order sirf existing position ko reduce ya close karega — nayi position nahi khol sakta.


post_only=True
rder sirf maker order ke roop me lagega — matlab yeh kabhi taker order nahi banega.
Limit orders for fee savings




```json
{
  "type": "batch_complete",
  "data": {
    "batch_id": "68f12aff3dfa2eec623ca58a",
    "summary": {
      "total_symbols": 3,
      "total_strategies": 5,
      "total_tasks": 15
    },
    "total_results": 3,
    "results": [
      {
        "symbol": "BTC-USD",
        "strategies": [
          {
            "strategy_name": "EMA Crossover Strategy",
            "symbol": "BTC-USD",
            "signal_type": "HOLD",
            "confidence": 0.0,
            "execution_time": 0.2759273052215576,
            "timestamp": "2025-10-16T17:26:26.215781+00:00",
            "price": 0.0,
            "created_at": "2025-10-16 17:27:27.059386+00:00",
            "_id": "68f12aff27dca72d9a3ca58a"
          },
          {
            "strategy_name": "RSI Oversold/Overbought Strategy",
            "symbol": "BTC-USD",
            "signal_type": "HOLD",
            "confidence": 0.0,
            "execution_time": 0.27466297149658203,
            "timestamp": "2025-10-16T17:26:26.215781+00:00",
            "price": 0.0,
            "created_at": "2025-10-16 17:27:27.059303+00:00",
            "_id": "68f12aff7a620e01da3ca58c"
          },
          {
            "strategy_name": "Bollinger Bands Mean Reversion Strategy",
            "symbol": "BTC-USD",
            "signal_type": "HOLD",
            "confidence": 0.0,
            "execution_time": 0.2602965831756592,
            "timestamp": "2025-10-16T17:26:26.215781+00:00",
            "price": 0.0,
            "created_at": "2025-10-16 17:27:27.047146+00:00",
            "_id": "68f12aff8b680056ab3ca58a"
          },
          {
            "strategy_name": "MACD Convergence Divergence Strategy",
            "symbol": "BTC-USD",
            "signal_type": "HOLD",
            "confidence": 0.0,
            "execution_time": 0.36953139305114746,
            "timestamp": "2025-10-16T17:26:26.215781+00:00",
            "price": 0.0,
            "created_at": "2025-10-16 17:27:27.157807+00:00",
            "_id": "68f12affcc5b501c1c3ca58b"
          },
          {
            "strategy_name": "Volume Breakout Strategy",
            "symbol": "BTC-USD",
            "signal_type": "HOLD",
            "confidence": 0.0,
            "execution_time": 0.3893008232116699,
            "timestamp": "2025-10-16T17:26:26.215781+00:00",
            "price": 0.0,
            "created_at": "2025-10-16 17:27:27.179676+00:00",
            "_id": "68f12affc270aff2853ca58b"
          }
        ]
      },
      {
        "symbol": "ETH-USD",
        "strategies": [
          {
            "strategy_name": "EMA Crossover Strategy",
            "symbol": "ETH-USD",
            "signal_type": "HOLD",
            "confidence": 0.0,
            "execution_time": 0.2605619430541992,
            "timestamp": "2025-10-16T17:26:26.215781+00:00",
            "price": 0.0,
            "created_at": "2025-10-16 17:27:27.052658+00:00",
            "_id": "68f12affa35bc12cbe3ca58c"
          },
          {
            "strategy_name": "RSI Oversold/Overbought Strategy",
            "symbol": "ETH-USD",
            "signal_type": "HOLD",
            "confidence": 0.0,
            "execution_time": 0.3476099967956543,
            "timestamp": "2025-10-16T17:26:26.215781+00:00",
            "price": 0.0,
            "created_at": "2025-10-16 17:27:27.141613+00:00",
            "_id": "68f12affec63c340313ca58a"
          },
          {
            "strategy_name": "Bollinger Bands Mean Reversion Strategy",
            "symbol": "ETH-USD",
            "signal_type": "HOLD",
            "confidence": 0.0,
            "execution_time": 0.3753986358642578,
            "timestamp": "2025-10-16T17:26:26.215781+00:00",
            "price": 0.0,
            "created_at": "2025-10-16 17:27:27.170632+00:00",
            "_id": "68f12affcbee700a563ca58b"
          },
          {
            "strategy_name": "MACD Convergence Divergence Strategy",
            "symbol": "ETH-USD",
            "signal_type": "HOLD",
            "confidence": 0.0,
            "execution_time": 0.25043630599975586,
            "timestamp": "2025-10-16T17:26:26.215781+00:00",
            "price": 0.0,
            "created_at": "2025-10-16 17:27:27.301804+00:00",
            "_id": "68f12aff8b680056ab3ca58b"
          },
          {
            "strategy_name": "Volume Breakout Strategy",
            "symbol": "ETH-USD",
            "signal_type": "HOLD",
            "confidence": 0.0,
            "execution_time": 0.18190217018127441,
            "timestamp": "2025-10-16T17:26:26.215781+00:00",
            "price": 0.0,
            "created_at": "2025-10-16 17:27:27.239263+00:00",
            "_id": "68f12affa35bc12cbe3ca58d"
          }
        ]
      },
      {
        "symbol": "SOL-USD",
        "strategies": [
          {
            "strategy_name": "EMA Crossover Strategy",
            "symbol": "SOL-USD",
            "signal_type": "HOLD",
            "confidence": 0.0,
            "execution_time": 0.3459963798522949,
            "timestamp": "2025-10-16T17:26:26.215781+00:00",
            "price": 0.0,
            "created_at": "2025-10-16 17:27:27.408315+00:00",
            "_id": "68f12aff27dca72d9a3ca58b"
          },
          {
            "strategy_name": "RSI Oversold/Overbought Strategy",
            "symbol": "SOL-USD",
            "signal_type": "HOLD",
            "confidence": 0.0,
            "execution_time": 0.3144261837005615,
            "timestamp": "2025-10-16T17:26:26.215781+00:00",
            "price": 0.0,
            "created_at": "2025-10-16 17:27:27.377541+00:00",
            "_id": "68f12aff7a620e01da3ca58d"
          },
          {
            "strategy_name": "Bollinger Bands Mean Reversion Strategy",
            "symbol": "SOL-USD",
            "signal_type": "HOLD",
            "confidence": 0.0,
            "execution_time": 0.2492384910583496,
            "timestamp": "2025-10-16T17:26:26.215781+00:00",
            "price": 0.0,
            "created_at": "2025-10-16 17:27:27.394229+00:00",
            "_id": "68f12affec63c340313ca58b"
          },
          {
            "strategy_name": "MACD Convergence Divergence Strategy",
            "symbol": "SOL-USD",
            "signal_type": "HOLD",
            "confidence": 0.0,
            "execution_time": 0.26671552658081055,
            "timestamp": "2025-10-16T17:26:26.215781+00:00",
            "price": 0.0,
            "created_at": "2025-10-16 17:27:27.426774+00:00",
            "_id": "68f12affcc5b501c1c3ca58c"
          },
          {
            "strategy_name": "Volume Breakout Strategy",
            "symbol": "SOL-USD",
            "signal_type": "HOLD",
            "confidence": 0.0,
            "execution_time": 0.23457121849060059,
            "timestamp": "2025-10-16T17:26:26.215781+00:00",
            "price": 0.0,
            "created_at": "2025-10-16 17:27:27.408123+00:00",
            "_id": "68f12affcbee700a563ca58c"
          }
        ]
      }
    ]
  }
}

```




```py

from app.delta_api import DeltaAPI
import time
from app.config import config

delta_api = DeltaAPI(
    base_url='https://api.india.delta.exchange',
    api_key=config.api_key,
    api_secret=config.api_secret,
    client_id=config.client_id
)

----------------------------- Emergency Exit ----------------------------- #
data = delta_api.emergency_exit()
print(data)


----------------------------- Get Balance ----------------------------- #
print("----------------------------- Get Balance -----------------------------")
balance = delta_api.get_balance()
print(f"Balance Response: {balance}")

# # Get current price from ticker

# ----------------------------- Create Entry, Stoploss, Target ----------------------------- #
ticker_data = delta_api.get_ticker("VFYUSD")
current_price = float(ticker_data.get('mark_price'))

# # Set order side (change this to "buy" or "sell" as needed)
order_side = "buy"  # Change to "buy" or "sell"

# # # Calculate entry, stoploss, and target prices based on side
entry_price = current_price  # Entry at current price

if order_side == "buy":
    stop_loss_price = current_price * 0.99 # 1% below current price
    edit_stoploss_price = current_price * 0.98 # 2% below current price
    target_price = current_price * 1.01 # 1% above current price
    edit_target_price = current_price * 1.02 # 2% above current price
else:
    stop_loss_price = current_price * 1.01 # 1% above current price
    edit_stoploss_price = current_price * 1.02 # 2% above current price
    target_price = current_price * 0.99 # 1% below current price
    edit_target_price = current_price * 0.98 # 2% below current price

print(f"Entry Price: ${entry_price}")
print(f"Stop Loss: ${stop_loss_price}")
print(f"Target: ${target_price}")

print("----------------------------- Create Entry, Stoploss, Target -----------------------------")
product_id = ticker_data.get('product_id')
if product_id:
    entry_resp = delta_api.create_entry(
        product_id=product_id,
        size=1,
        side=order_side,
        entry_price=entry_price,
        leverage=20
    )
    print("Entry response:")
    print(entry_resp)


    #  STOPLOSS AND TARGET
    time.sleep(20)
    st_resp = delta_api.create_stoploss_target(
        product_id=product_id,
        symbol=ticker_data.get('symbol'),
        stoploss_price=stop_loss_price,
        target_price=target_price,
    )
    print("Stoploss/Target response:")
    print(st_resp)


    time.sleep(10)

    edit_resp = delta_api.edit_stoploss_target(
        order_id = st_resp.get('stop_loss_order').get('id'),
        product_id = product_id,
        symbol = ticker_data.get('symbol'),
        stoploss_price = edit_stoploss_price,
        target_price = edit_target_price,
    )
    print("Edit response:")
    print(edit_resp)

    time.sleep(5)

    print("----------------------------- Get All Open Orders -----------------------------")


    all_open_orders = delta_api.get_all_open_orders()
    print(f"All open orders: {all_open_orders}")

    time.sleep(5)

    print("----------------------------- Get All Open Positions -----------------------------")

    all_open_positions = delta_api.get_all_open_positions()
    print(f"All open positions: {all_open_positions}")


    time.sleep(5)

    print("----------------------------- Emergency Exit -----------------------------")

    emergency_exit = delta_api.emergency_exit()
    print(f"Emergency exit: {emergency_exit}")



```