Personal Budget Dashboard

A simple, local-first personal finance tracking system using Telegram for data entry and Streamlit for visualization. All data is stored locally in an SQLite database. Remote access is possible via Tailscale.

This is a personal pet project for tracking finances using Telegram and Streamlit, developed with AI assistance.

Features:
- Add income and expenses via Telegram bot
- View analytics in a Streamlit dashboard
- Data never leaves your machine
- Works on Windows, Linux, and macOS

Requirements:
- Python 3.9 or higher
- Internet connection (for Telegram and optional Tailscale access)

Installation:

1. Clone this repository:
   git clone https://github.com/your-username/personal-budget-dashboard.git
   cd personal-budget-dashboard

2. Install dependencies:
   pip install -r requirements.txt

3. Set up the Telegram bot:
   - Create a bot via @BotFather on Telegram
   - Open TG_Budget_Bot.py and replace "YOUR_TELEGRAM_BOT_TOKEN_HERE" with your actual token

4. Start the Telegram bot:
   python TG_Budget_Bot.py

5. Start the dashboard:
   streamlit run Streamlit_Budget_Bot.py --server.port=8501 --server.address=0.0.0.0

Usage:

Send messages to your Telegram bot in one of these formats:
- category, amount
- category, amount, comment

Examples:
- groceries, 450
- salary, -60000, monthly payment

Note: 
- Expenses are positive numbers
- Income is entered as negative numbers

The database file (Budget_DB.db) is created automatically on the first message.

Security:

- All data remains on your local machine
- No cloud services are used
- Remote access requires Tailscale (optional and user-configured)

Project Structure:

Streamlit_Budget_Bot.py          — Streamlit dashboard
TG_Budget_Bot.py          — Telegram bot
requirements.txt — Python dependencies
README.md       — This file


The Budget_DB.db file is not included in the repository and is generated automatically.

Its easy to use, by Telegram you add data to DB, when it will be shown in streamlit with good UI
Also, if you want to see it jn other devices- you can use Tailscale

