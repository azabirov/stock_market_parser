#!/usr/bin/env python3
"""
Stock Parser Script

This script fetches stock data from the Tinkoff Invest API and stores it in a PostgreSQL database.
It continuously runs in the background, handling both classic and weekend stocks, and logs its operations.
"""

import os
import logging
import traceback
from tinkoff.invest import Client, CandleInterval, InstrumentStatus, SecurityTradingStatus
from tinkoff.invest.exceptions import RequestError
from grpc import StatusCode
import psycopg2
from datetime import datetime, timedelta
import pytz
import asyncio
from dateutil import parser
import time

# ---------------------------
# Logging Configuration
# ---------------------------

os.makedirs('logs', exist_ok=True) # Ensure the logs directory exists

LOG_FILE = os.path.join('logs', 'stock_parser.log')
ERROR_LOG_FILE = os.path.join('logs', 'stock_parser_error.log')

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.DEBUG,  # Set to DEBUG for detailed logs
    format='%(asctime)s - %(levelname)s - %(message)s',
)

# Configure a separate logger for errors
error_handler = logging.FileHandler(ERROR_LOG_FILE)
error_handler.setLevel(logging.ERROR)
error_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
error_handler.setFormatter(error_formatter)
logging.getLogger().addHandler(error_handler)

logging.info("Starting stock_parser script.")

# ---------------------------
# Load Environment Variables
# ---------------------------

API_TOKEN = os.getenv('API_TOKEN')
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_NAME = os.getenv('DB_NAME', 'quantify_moex_stocks')
DB_USER = os.getenv('DB_USER', 'quantify_system_account')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_PORT = os.getenv('DB_PORT', '5432')

logging.info(f"API_TOKEN is {'set' if API_TOKEN else 'not set'}.")
logging.info(f"Database Host: {DB_HOST}")
logging.info(f"Database Name: {DB_NAME}")
logging.info(f"Database User: {DB_USER}")

# ---------------------------
# Timezone Configuration
# ---------------------------

MOSCOW_TZ = pytz.timezone('Europe/Moscow')

# ---------------------------
# Database Connection Function
# ---------------------------

def get_db_connection():
    """
    Establishes a connection to the PostgreSQL database.

    Returns:
        psycopg2.extensions.connection: Database connection object.

    Raises:
        Exception: If the connection fails.
    """
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        logging.info("Database connection successful.")
        return conn
    except Exception as e:
        logging.error(f"Database connection failed: {e}")
        logging.error(traceback.format_exc())
        raise

# ---------------------------
# Function to Store Candle Data
# ---------------------------

def store_candle_in_db(candle, ticker, table_name):
    """
    Stores a single candle's data into the specified database table.

    Args:
        candle: The candle data fetched from the API.
        ticker (str): The stock ticker symbol.
        table_name (str): The target database table name.

    Raises:
        Exception: If storing data fails.
    """
    try:
        logging.debug(f"Candle.time: {candle.time} (Type: {type(candle.time)})")
        
        # Convert candle.time to datetime object
        if isinstance(candle.time, datetime):
            begin_time = candle.time
        elif isinstance(candle.time, str):
            begin_time = parser.isoparse(candle.time)
        else:
            logging.error(f"Unsupported type for candle.time: {type(candle.time)}")
            return  # Skip this candle
        
        logging.debug(f"Converted begin_time: {begin_time} (Type: {type(begin_time)})")
        
        close_time = begin_time + timedelta(minutes=10)
        logging.debug(f"Calculated close_time: {close_time} (Type: {type(close_time)})")

        conn = get_db_connection()
        cursor = conn.cursor()

        query = f"""
        INSERT INTO {table_name} (ticker, begin_time, close_time, open, high, low, close)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (ticker, begin_time) DO NOTHING;
        """
        cursor.execute(
            query,
            (
                ticker,
                begin_time,
                close_time,
                candle.open.units + candle.open.nano / 1e9,
                candle.high.units + candle.high.nano / 1e9,
                candle.low.units + candle.low.nano / 1e9,
                candle.close.units + candle.close.nano / 1e9,
            ),
        )
        conn.commit()
        cursor.close()
        conn.close()
        logging.info(f"Stored candle data for {ticker} in {table_name}.")

    except Exception as e:
        logging.error(f"Failed to store candle data for {ticker}: {e}")
        logging.error(traceback.format_exc())

# ---------------------------
# Function to Retrieve Stock Lists
# ---------------------------

def get_stock_lists():
    """
    Retrieves lists of classic and weekend stock FIGIs from the Tinkoff API.

    Returns:
        tuple: Two lists containing FIGIs for classic and weekend stocks respectively.
    """
    try:
        with Client(API_TOKEN) as client:
            instruments = client.instruments.shares(instrument_status=InstrumentStatus.INSTRUMENT_STATUS_BASE)

            # Log all instruments for debugging
            for instrument in instruments.instruments:
                logging.debug(f"Instrument: {instrument}")

            # Filter based on trading status
            classic_stocks = [
                instrument.figi for instrument in instruments.instruments
                if instrument.trading_status in [
                    SecurityTradingStatus.SECURITY_TRADING_STATUS_NORMAL_TRADING,
                    SecurityTradingStatus.SECURITY_TRADING_STATUS_BREAK_IN_TRADING
                ]
            ]

            weekend_stocks = [
                instrument.figi for instrument in instruments.instruments
                if getattr(instrument, 'weekend_flag', False)  # Use getattr to avoid AttributeError
            ]

            logging.info(f"Retrieved {len(classic_stocks)} classic and {len(weekend_stocks)} weekend stocks.")
            return classic_stocks, weekend_stocks

    except Exception as e:
        logging.error(f"Failed to retrieve stock lists: {e}")
        logging.error(traceback.format_exc())
        return [], []

# ---------------------------
# Function to Fetch and Store Candles
# ---------------------------

def fetch_and_store(tickers, table_name, interval):
    """
    Fetches candles for the given tickers and stores them in the database.

    Args:
        tickers (list): List of stock FIGIs to fetch candles for.
        table_name (str): Target database table name.
        interval: Interval between candles.

    Raises:
        Exception: If fetching or storing candles fails.
    """
    try:
        with Client(API_TOKEN) as client:
            for ticker in tickers:
                now = datetime.now(tz=MOSCOW_TZ)
                from_time = now - timedelta(minutes=10)  # Fetch candles from the last 10 minutes

                # For logging purposes
                from_time_iso = from_time.isoformat()
                now_iso = now.isoformat()

                logging.info(f"Fetching candles for {ticker} from {from_time_iso} to {now_iso}")

                try:
                    # Pass datetime objects directly to get_candles
                    candles = client.market_data.get_candles(
                        figi=ticker,
                        from_=from_time,
                        to=now,
                        interval=interval
                    ).candles

                    logging.debug(f"Number of candles fetched for {ticker}: {len(candles)}")

                    for candle in candles:
                        logging.debug(f"Processing candle: {candle}")
                        store_candle_in_db(candle, ticker, table_name)
                        logging.info(f"Candle data: {candle}")

                    # Optional: Sleep after each successful request to avoid hitting rate limits
                    time.sleep(0.1)  # Adjust sleep time as needed

                except RequestError as re:
                    if re.status_code == StatusCode.RESOURCE_EXHAUSTED:
                        reset_time = int(re.metadata.get('ratelimit_reset', 60))  # Default to 60 seconds
                        logging.warning(f"Rate limit exceeded for {ticker}. Sleeping for {reset_time} seconds.")
                        time.sleep(reset_time)
                        # Retry the same ticker after sleeping
                        try:
                            candles = client.market_data.get_candles(
                                figi=ticker,
                                from_=from_time,
                                to=now,
                                interval=interval
                            ).candles

                            logging.debug(f"Number of candles fetched for {ticker} after retry: {len(candles)}")

                            for candle in candles:
                                logging.debug(f"Processing candle: {candle}")
                                store_candle_in_db(candle, ticker, table_name)
                                logging.info(f"Candle data: {candle}")

                        except RequestError as re_retry:
                            logging.error(f"Retry failed for {ticker}: {re_retry}")
                            logging.error(traceback.format_exc())
                        except Exception as e_retry:
                            logging.error(f"An unexpected error occurred during retry for {ticker}: {e_retry}")
                            logging.error(traceback.format_exc())
                    else:
                        logging.error(f"Failed to fetch candles for {ticker}: {re}")
                        logging.error(traceback.format_exc())
                except Exception as e:
                    logging.error(f"An unexpected error occurred while fetching candles for {ticker}: {e}")
                    logging.error(traceback.format_exc())

    except Exception as e:
        logging.error(f"Failed to fetch and store candles: {e}")
        logging.error(traceback.format_exc())

# ---------------------------
# Async Scheduler Function
# ---------------------------

async def scheduler():
    """
    Asynchronous scheduler that periodically fetches and stores stock candles based on the current time and weekday.
    """
    while True:
        try:
            now = datetime.now(tz=MOSCOW_TZ)
            weekday = now.weekday()
            hour = now.hour

            classic_stocks, weekend_stocks = get_stock_lists()

            if weekday < 5 and 10 <= hour < 23:
                fetch_and_store(classic_stocks, 'classic_stocks', CandleInterval.CANDLE_INTERVAL_10_MIN)

            if 10 <= hour < 23:
                fetch_and_store(weekend_stocks, 'weekend_stocks', CandleInterval.CANDLE_INTERVAL_10_MIN)

            # Calculate sleep time until next 10-minute interval
            now = datetime.now()
            sleep_minutes = 10 - (now.minute % 10)
            sleep_seconds = sleep_minutes * 60 - now.second
            logging.debug(f"Sleeping for {sleep_seconds} seconds until next interval.")
            await asyncio.sleep(sleep_seconds)
        except Exception as e:
            logging.error(f"Scheduler encountered an error: {e}")
            logging.error(traceback.format_exc())
            # Optional: Sleep for a short duration before retrying to prevent rapid failure loops
            await asyncio.sleep(60)

# ---------------------------
# Main Execution Block
# ---------------------------

if __name__ == '__main__':
    """
    Entry point of the stock_parser script. Initiates the asynchronous scheduler.
    """
    try:
        asyncio.run(scheduler())
    except KeyboardInterrupt:
        logging.info("Script terminated by user.")
    except Exception as e:
        logging.error(f"Script failed unexpectedly: {e}")
        logging.error(traceback.format_exc())
