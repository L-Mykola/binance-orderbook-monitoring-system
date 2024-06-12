# Binance Orderbook Monitoring System

This system is designed to monitor the orderbook for selected cryptocurrency pairs (BTC/USDT, ETH/USDT, and SOL/USDT) on the Binance exchange. It calculates the order volumes at +2% and -2% price levels from the current price, stores the data in a database, and sends notifications to a Telegram group when the current order volumes deviate significantly from the volume-weighted average values over a specified period.

## Features

- **Binance Exchange Connection:** The system connects to the Binance exchange using the official Binance Python API client (`python-binance`) to receive real-time orderbook data for the specified currency pairs.
- **Order Volume Calculation:** For each received orderbook update, the system calculates the order volumes at +2% and -2% distance from the current price (the midpoint between the best bid and best ask).
- **Data Storage:** The calculated order volume data is stored in a database using a custom database handler module.
- **Telegram Notifications:** If the current order volume deviates significantly from the volume-weighted average value over a specified period, a notification is sent to a designated Telegram group using the `python-telegram-bot` library.
- **Parallel Data Processing:** The system processes data from different currency pairs in parallel using asyncio tasks.
- **Configuration Management:** System parameters, such as Binance API keys, database connection details, notification thresholds, and Telegram bot settings, are loaded from a `settings.json` file.
- **Performance Monitoring:** The system logs information about significant order volume deviations to the `performance.log` file.

## System Architecture

The system consists of the following main components:

- **Binance API Client:** Establishes a connection with the Binance exchange using the `AsyncClient` class from the `python-binance` library and retrieves real-time orderbook data.
- **Order Volume Calculator:** Calculates the order volumes at specific price levels (+2% and -2%) based on the received orderbook data.
- **Data Storage Module:** Handles the storage of calculated order volume data in the configured database using the `insert_into_table` function from the `db_handler` module.
- **Anomaly Detection:** Computes the volume-weighted average values over the specified period using the `get_values` function from the `db_handler` module and detects significant deviations in the current order volumes.
- **Notification Module:** Generates and sends notifications to the designated Telegram group using the `python-telegram-bot` library when anomalies are detected.
- **Parallel Processing:** Implements parallel processing using asyncio tasks to handle data processing for multiple currency pairs concurrently.
- **Configuration Manager:** Loads system configurations from the `settings.json` file.
- **Performance Monitoring:** Logs information about significant order volume deviations to the `performance.log` file.

## Installation and Setup

1. Clone the project repository:

```bash
git clone https://github.com/L-Mykola/binance-orderbook-monitoring-system.git
```

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

3. Configure the system by creating a `settings.json` file with the following structure:
```bash
{
  "binance_api_key": "YOUR_BINANCE_API_KEY",
  "binance_secret_key": "YOUR_BINANCE_SECRET_KEY",
  "database_connection": {"host": "YOUR_HOST",  "user": "YOUR_USERNAME", "password": "YOUR_PASSWORD"},
  "database_name": "YOUR_DATABASE_NAME",
  "period_of_time": PERIOD_FOR_CHEKING_VOLUME_DEVIATIONS_IN_MINUTES ,
  "vol_diff_limit": VOLUME_DEVIATION_LIMIT_IN_PERCENTAGE_TERMS,
  "tg_bot_token": "YOUR_TELEGRAM_BOT_TOKEN",
  "tg_chat_id": "YOUR_TELEGRAM_CHAT_ID"
}
```
5. Run the system:
```bash
python main.py
```

The system will start monitoring the orderbook for the specified currency pairs and send notifications to the designated Telegram group when anomalies are detected.
