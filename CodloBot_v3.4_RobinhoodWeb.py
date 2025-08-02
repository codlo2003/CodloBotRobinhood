# CodloBot v3.4 - Robinhood Web Edition
# Runs as a Render Web Service (free tier) with a keep-alive Flask server

import yfinance as yf
import pandas as pd
import smtplib
from email.mime.text import MIMEText
import datetime
import json
import time
import sys
from flask import Flask
import threading

# === Load Config ===
CONFIG_FILE = "config.txt"
with open(CONFIG_FILE, "r") as f:
    config = json.load(f)

TICKERS = config["tickers"]
EMAIL = config["email"]
PASSWORD = config["password"]
TO_EMAIL = config["to_email"]
TO_SMS = config["to_sms"]
LOGFILE = "codlobot_robinhood_web_logs.log"

# === Flask Keep-Alive Server ===
app = Flask(__name__)
@app.route('/')
def home():
    return "🚀 CodloBot v3.4 is alive and running!"

def start_flask():
    app.run(host="0.0.0.0", port=8080)

# === Indicators ===
def compute_rsi(series, period=14):
    delta = series.diff()
    gain = delta.where(delta > 0, 0).rolling(period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def compute_macd(series, short=12, long=26, signal=9):
    exp1 = series.ewm(span=short, adjust=False).mean()
    exp2 = series.ewm(span=long, adjust=False).mean()
    macd = exp1 - exp2
    sig = macd.ewm(span=signal, adjust=False).mean()
    return macd, sig

# === Signal Logic ===
def check_signal(symbol):
    try:
        df = yf.download(symbol, period="6mo", interval="1d", progress=False)
        df['RSI'] = compute_rsi(df['Close'])
        df['MA50'] = df['Close'].rolling(50).mean()
        df['MACD'], df['Signal'] = compute_macd(df['Close'])
        df.dropna(inplace=True)
        if df.empty:
            return None
        latest = df.iloc[-1]
        close = float(latest['Close'])
        ma50 = float(latest['MA50'])
        rsi = float(latest['RSI'])
        macd = float(latest['MACD'])
        signal_line = float(latest['Signal'])
        if (close > ma50) and (50 < rsi < 70) and (macd > signal_line):
            return f"🚀 BUY: {symbol} (Robinhood) at ${close:.4f}"
        elif (rsi > 70) or (close < ma50):
            return f"⚠️ SELL: {symbol} (Robinhood) at ${close:.4f}"
    except Exception as e:
        print(f"❌ Error for {symbol}: {e}", file=sys.stderr)
    return None

# === Email Alert ===
def send_alert(message):
    msg = MIMEText(message)
    msg['Subject'] = "📈 CodloBot Robinhood Alert"
    msg['From'] = EMAIL
    msg['To'] = TO_EMAIL
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL, PASSWORD)
            server.sendmail(EMAIL, [TO_EMAIL, TO_SMS], msg.as_string())
    except Exception as e:
        print(f"❌ Email sending failed: {e}", file=sys.stderr)

def log_alert(message):
    with open(LOGFILE, "a") as f:
        f.write(f"{datetime.datetime.now()} - {message}\n")

# === Bot Logic ===
def run_bot():
    alerts = []
    for ticker in TICKERS:
        signal = check_signal(ticker)
        if signal:
            alerts.append(signal)
    if alerts:
        alert_msg = "\n".join(alerts)
        send_alert(alert_msg)
        log_alert(alert_msg)
        print("✅ Alerts Sent:\n", alert_msg)
    else:
        print("No signals at this time.")

# === Main Runner with Loop ===
def main_loop():
    print("🚀 CodloBot v3.4 (Robinhood Web Edition) is running with Flask keep-alive.")
    while True:
        run_bot()
        print("⏳ Sleeping 15 minutes...")
        time.sleep(900)

if __name__ == "__main__":
    threading.Thread(target=start_flask).start()
    main_loop()
