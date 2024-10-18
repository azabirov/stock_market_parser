#!/usr/bin/env python3
"""
Query Data Script

This script allows users to query and display stored stock data from the PostgreSQL database.
It supports both command-line arguments and an interactive menu for flexibility.
"""

import os
import psycopg2
import argparse
from tabulate import tabulate
from datetime import datetime

def get_db_connection():
    """
    Establishes a connection to the PostgreSQL database.

    Returns:
        psycopg2.extensions.connection: Database connection object.

    Raises:
        SystemExit: If the connection fails.
    """
    try:
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            database=os.getenv('DB_NAME', 'quantify_moex_stocks'),
            user=os.getenv('DB_USER', 'quantify_system_account'),
            password=os.getenv('DB_PASSWORD'),
            port=os.getenv('DB_PORT', '5432')
        )
        return conn
    except Exception as e:
        print(f"Error connecting to the database: {e}")
        exit(1)

def query_table(conn, table, limit, ticker=None, start_date=None, end_date=None):
    """
    Executes a query on the specified table with optional filters and displays the results.

    Args:
        conn: Database connection object.
        table (str): Name of the table to query.
        limit (int): Number of records to fetch.
        ticker (str, optional): Ticker symbol to filter by.
        start_date (datetime, optional): Start date for filtering records.
        end_date (datetime, optional): End date for filtering records.
    """
    try:
        cursor = conn.cursor()
        query = f"SELECT * FROM {table}"
        conditions = []
        params = []

        if ticker:
            conditions.append("ticker = %s")
            params.append(ticker)
        if start_date:
            conditions.append("begin_time >= %s")
            params.append(start_date)
        if end_date:
            conditions.append("begin_time <= %s")
            params.append(end_date)

        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        query += f" ORDER BY begin_time DESC LIMIT %s;"
        params.append(limit)

        cursor.execute(query, tuple(params))
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]

        if rows:
            print(tabulate(rows, headers=columns, tablefmt="psql"))
        else:
            print("No records found with the specified criteria.")

        cursor.close()
    except Exception as e:
        print(f"Error querying the table: {e}")
        exit(1)

def parse_arguments():
    """
    Parses command-line arguments provided by the user.

    Returns:
        argparse.Namespace: Parsed arguments.
    """
    parser = argparse.ArgumentParser(description="Query stock data from the PostgreSQL database.")
    parser.add_argument(
        '-t', '--table',
        type=str,
        choices=['classic_stocks', 'weekend_stocks'],
        required=True,
        help="Specify the table to query: 'classic_stocks' or 'weekend_stocks'."
    )
    parser.add_argument(
        '-l', '--limit',
        type=int,
        default=10,
        help="Number of records to fetch (default: 10)."
    )
    parser.add_argument(
        '-k', '--ticker',
        type=str,
        help="Filter by ticker symbol."
    )
    parser.add_argument(
        '-s', '--start_date',
        type=str,
        help="Filter records from this date (inclusive). Format: YYYY-MM-DD"
    )
    parser.add_argument(
        '-e', '--end_date',
        type=str,
        help="Filter records up to this date (inclusive). Format: YYYY-MM-DD"
    )
    return parser.parse_args()

def validate_date(date_text):
    """
    Validates and converts a date string to a datetime object.

    Args:
        date_text (str): Date string in 'YYYY-MM-DD' format.

    Returns:
        datetime: Parsed datetime object.

    Raises:
        SystemExit: If the date format is incorrect.
    """
    try:
        return datetime.strptime(date_text, '%Y-%m-%d')
    except ValueError:
        print(f"Incorrect date format for '{date_text}'. Expected format: YYYY-MM-DD")
        exit(1)

def interactive_menu():
    """
    Presents an interactive menu to the user for querying data without command-line arguments.
    """
    print("=== Stock Data Query Menu ===")
    print("1. Query Classic Stocks")
    print("2. Query Weekend Stocks")
    print("3. Exit")
    choice = input("Enter your choice (1-3): ")

    if choice == '1':
        table = 'classic_stocks'
    elif choice == '2':
        table = 'weekend_stocks'
    elif choice == '3':
        print("Exiting the program.")
        exit(0)
    else:
        print("Invalid choice. Please try again.")
        interactive_menu()
        return

    try:
        limit_input = input("Enter the number of records to fetch (default 10): ")
        limit = int(limit_input) if limit_input else 10
    except ValueError:
        print("Invalid input for limit. Using default value of 10.")
        limit = 10

    ticker = input("Enter ticker symbol to filter (leave blank for no filter): ") or None
    start_date_input = input("Enter start date (YYYY-MM-DD) to filter (leave blank for no filter): ") or None
    end_date_input = input("Enter end date (YYYY-MM-DD) to filter (leave blank for no filter): ") or None

    start_date = validate_date(start_date_input) if start_date_input else None
    end_date = validate_date(end_date_input) if end_date_input else None

    conn = get_db_connection()
    query_table(conn, table, limit, ticker, start_date, end_date)
    conn.close()

def main():
    """
    Main function to execute the query script based on user input or command-line arguments.
    """
    try:
        import sys
        from tabulate import tabulate
    except ImportError:
        print("Required packages are not installed. Please install them using 'pip install tabulate'.")
        exit(1)

    if len(sys.argv) > 1:
        args = parse_arguments()

        if args.start_date:
            args.start_date = validate_date(args.start_date)
        if args.end_date:
            args.end_date = validate_date(args.end_date)

        conn = get_db_connection()
        query_table(conn, args.table, args.limit, args.ticker, args.start_date, args.end_date)
        conn.close()
    else:
        interactive_menu()

if __name__ == "__main__":
    main()
