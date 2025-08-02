# CodloBot v3.4 - Robinhood Web Edition

## ✅ Features
- Monitors only Robinhood-supported cryptos.
- Sends alerts via Email + SMS.
- Includes a Flask web server for Render free hosting.
- Runs continuously and checks every 15 minutes.

## 🚀 Deployment (Render Web Service - Free)
1. Push files to a GitHub repo.
2. On Render, create a **Web Service** (not Worker).
3. Build Command:
   pip install -r requirements.txt
4. Start Command:
   python CodloBot_v3.4_RobinhoodWeb.py
5. Deploy → Visit the URL to confirm Flask is running → Bot works in background.

## 🌐 Flask Endpoint
- Visiting the Render URL (e.g., https://yourbot.onrender.com) will show "CodloBot is alive!" to keep it awake.
