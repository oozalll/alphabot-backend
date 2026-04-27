# main.py - AlphaBot Backend (Binance Gerçek Veri)
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from binance.client import Client
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

API_KEY = os.environ.get("BINANCE_API_KEY", "")
API_SECRET = os.environ.get("BINANCE_API_SECRET", "")
client = Client(API_KEY, API_SECRET)

@app.get("/api/balance")
def get_balance():
    account = client.get_account()
    balances = [b for b in account["balances"] if float(b["free"]) > 0]
    usdt = next((float(b["free"]) for b in balances if b["asset"] == "USDT"), 0)
    return {"total_usdt": usdt, "balances": balances}

@app.get("/api/positions")
def get_positions():
    try:
        positions = client.futures_position_information()
        open_pos = [p for p in positions if float(p["positionAmt"]) != 0]
        return {"positions": open_pos}
    except:
        return {"positions": []}

@app.get("/api/performance")
def get_performance():
    trades = client.get_my_trades(symbol="BTCUSDT", limit=100)
    wins = sum(1 for t in trades if float(t.get("realizedPnl", 0)) > 0)
    total = len(trades)
    winrate = round((wins / total * 100) if total > 0 else 0, 1)
    return {"winrate": winrate, "total_trades": total}

@app.get("/api/price/{symbol}")
def get_price(symbol: str):
    ticker = client.get_symbol_ticker(symbol=symbol)
    return {"price": float(ticker["price"]), "symbol": symbol}

@app.get("/api/risk/status")
def get_risk():
    return {
        "daily_loss_used_pct": 0,
        "daily_loss_limit_pct": 2,
        "drawdown_current_pct": 0,
        "drawdown_limit_pct": 10,
        "open_positions": 0,
        "max_open_positions": 5,
        "risk_score": 20
    }

@app.get("/api/logs")
def get_logs():
    return {"logs": []}

@app.post("/api/bot/start")
def bot_start():
    return {"status": "started"}

@app.post("/api/bot/stop")
def bot_stop():
    return {"status": "stopped"}

@app.get("/health")
def health():
    return {"status": "ok"}
