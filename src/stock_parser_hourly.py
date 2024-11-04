#!/usr/bin/env python3
"""
Hourly Stock Parser Script

This script fetches stock data from the Tinkoff Invest API every hour and stores it in a PostgreSQL database.
It runs alongside the main stock parser but with hourly intervals instead of 10-minute intervals.
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

os.makedirs('logs', exist_ok=True)

LOG_FILE = os.path.join('logs', 'stock_parser_hourly.log')
ERROR_LOG_FILE = os.path.join('logs', 'stock_parser_hourly_error.log')

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
)

error_handler = logging.FileHandler(ERROR_LOG_FILE)
error_handler.setLevel(logging.ERROR)
error_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
error_handler.setFormatter(error_formatter)
logging.getLogger().addHandler(error_handler)

logging.info("Starting hourly stock parser script.")

# Load environment variables from the original parser
API_TOKEN = os.getenv('API_TOKEN')
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_NAME = os.getenv('DB_NAME', 'quantify_moex_stocks')
DB_USER = os.getenv('DB_USER', 'quantify_system_account')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_PORT = os.getenv('DB_PORT', '5432')

# Use the same timezone configuration
MOSCOW_TZ = pytz.timezone('Europe/Moscow')

# Use the same database connection function from stock_parser.py
def get_db_connection():
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

def fetch_and_store(stock_dict, table_name, interval):
    """Fetches and stores hourly candle data for given stocks."""
    try:
        with Client(API_TOKEN) as client:
            for figi, ticker in stock_dict.items():
                now = datetime.now(tz=MOSCOW_TZ)
                from_time = now - timedelta(hours=2)  # Fetch last 2 hours of data
                
                from_time_iso = from_time.isoformat()
                now_iso = now.isoformat()
                
                logging.info(f"Fetching candles for {ticker} (FIGI: {figi}) from {from_time_iso} to {now_iso}")

                try:
                    candles = client.market_data.get_candles(
                        figi=figi,
                        from_=from_time,
                        to=now,
                        interval=interval
                    ).candles

                    logging.debug(f"Number of candles fetched for {ticker}: {len(candles)}")

                    for candle in candles:
                        logging.debug(f"Processing candle: {candle}")
                        store_candle_in_db(candle, figi, ticker, table_name)
                        logging.info(f"Candle data: {candle}")

                    time.sleep(0.1)  # Rate limiting

                except RequestError as re:
                    if re.status_code == StatusCode.RESOURCE_EXHAUSTED:
                        reset_time = int(re.metadata.get('ratelimit_reset', 60))
                        logging.warning(f"Rate limit exceeded for {ticker}. Sleeping for {reset_time} seconds.")
                        time.sleep(reset_time)
                        # Add retry logic here (same as original script)
                    else:
                        logging.error(f"Failed to fetch candles for {ticker}: {re}")
                        logging.error(traceback.format_exc())
                except Exception as e:
                    logging.error(f"An unexpected error occurred while fetching candles for {ticker}: {e}")
                    logging.error(traceback.format_exc())

    except Exception as e:
        logging.error(f"Failed to fetch and store candles: {e}")
        logging.error(traceback.format_exc())

async def scheduler():
    """
    Asynchronous scheduler that periodically fetches and stores stock candles hourly.
    """
    while True:
        try:
            now = datetime.now(tz=MOSCOW_TZ)
            classic_stocks, weekend_stocks = get_stock_lists()

            if now.weekday() < 5:  # Monday to Friday
                fetch_and_store(classic_stocks, 'classic_stocks_hourly', CandleInterval.CANDLE_INTERVAL_HOUR)

            if 10 <= now.hour < 23:
                fetch_and_store(weekend_stocks, 'weekend_stocks_hourly', CandleInterval.CANDLE_INTERVAL_HOUR)

            # Calculate sleep time until next hour
            now = datetime.now()
            sleep_minutes = 60 - now.minute
            sleep_seconds = sleep_minutes * 60 - now.second
            logging.debug(f"Sleeping for {sleep_seconds} seconds until next hour.")
            await asyncio.sleep(sleep_seconds)
        except Exception as e:
            logging.error(f"Scheduler encountered an error: {e}")
            logging.error(traceback.format_exc())
            await asyncio.sleep(60)


def get_stock_lists():
    """
    Retrieves lists of classic and weekend stock FIGIs and tickers from the Tinkoff API.

    Returns:
        tuple: Two dictionaries containing FIGI to ticker mappings for classic and weekend stocks respectively.
    """
    try:
        with Client(API_TOKEN) as client:
            instruments = client.instruments.shares(instrument_status=InstrumentStatus.INSTRUMENT_STATUS_BASE)

            # Log all instruments for debugging
            for instrument in instruments.instruments:
                logging.debug(f"Instrument: {instrument}")

            # Filter based on trading status
            classic_stocks = {
                instrument.figi: instrument.ticker for instrument in instruments.instruments
                if instrument.trading_status in [
                    SecurityTradingStatus.SECURITY_TRADING_STATUS_NORMAL_TRADING,
                    SecurityTradingStatus.SECURITY_TRADING_STATUS_NOT_AVAILABLE_FOR_TRADING
                ]
            }

            weekend_stocks = {
                instrument.figi: instrument.ticker for instrument in instruments.instruments
                if getattr(instrument, 'weekend_flag', False)  # Use getattr to avoid AttributeError
            }

            logging.info(f"Retrieved {len(classic_stocks)} classic and {len(weekend_stocks)} weekend stocks.")
            return classic_stocks, weekend_stocks

    except Exception as e:
        logging.error(f"Failed to retrieve stock lists: {e}")
        logging.error(traceback.format_exc())
        return {}, {}
    
    
def initialize_tables(conn):
    """Creates the necessary tables if they don't exist."""
    try:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS classic_stocks_hourly (
                    id SERIAL PRIMARY KEY,
                    ticker VARCHAR(20),
                    begin_time TIMESTAMPTZ,
                    close_time TIMESTAMPTZ,
                    open NUMERIC(12, 6),
                    high NUMERIC(12, 6),
                    low NUMERIC(12, 6),
                    close NUMERIC(12, 6),
                    UNIQUE (ticker, begin_time)
                );

                CREATE TABLE IF NOT EXISTS weekend_stocks_hourly (
                    id SERIAL PRIMARY KEY,
                    ticker VARCHAR(20),
                    begin_time TIMESTAMPTZ,
                    close_time TIMESTAMPTZ,
                    open NUMERIC(12, 6),
                    high NUMERIC(12, 6),
                    low NUMERIC(12, 6),
                    close NUMERIC(12, 6),
                    UNIQUE (ticker, begin_time)
                );
            """)
            conn.commit()
            logging.info("Database tables initialized successfully.")
    except Exception as e:
        logging.error(f"Error initializing tables: {e}")
        logging.error(traceback.format_exc())
        raise

def store_candle_in_db(candle, figi, ticker, table_name):
    """
    Stores a single candle's data into the specified database table.
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
            return
        
        logging.debug(f"Converted begin_time: {begin_time} (Type: {type(begin_time)})")
        
        close_time = begin_time + timedelta(hours=1)  # Changed from 10 minutes to 1 hour
        logging.debug(f"Calculated close_time: {close_time} (Type: {type(close_time)})")

        with get_db_connection() as conn:
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
            logging.info(f"Stored candle data for {ticker} in {table_name}.")

    except Exception as e:
        logging.error(f"Failed to store candle data for {ticker}: {e}")
        logging.error(traceback.format_exc())

if __name__ == '__main__':
    try:
        # Initialize database tables
        with get_db_connection() as conn:
            initialize_tables(conn)
        
        # Start the scheduler
        asyncio.run(scheduler())
    except KeyboardInterrupt:
        logging.info("Script terminated by user.")
    except Exception as e:
        logging.error(f"Script failed unexpectedly: {e}")
        logging.error(traceback.format_exc())