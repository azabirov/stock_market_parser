# Tinkoff Russian Stock Market Parser

## Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
  - [Running the Stock Parser](#running-the-stock-parser)
  - [Querying the Database](#querying-the-database)
- [Database Schema](#database-schema)
- [Logging](#logging)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

## Overview

The **Stock Parser Project** is a Python-based application designed to fetch stock data from the [Tinkoff Invest API](https://tinkoff.github.io/investAPI/) and store it in a PostgreSQL database. The project comprises two primary scripts:

1. **`stock_parser.py`**: Continuously fetches and stores stock data.
2. **`query_data.py`**: Allows users to query and display stored stock data.

By leveraging a virtual environment and environment variables for configuration, the project ensures secure and manageable operations.

## Features

- **Automated Data Collection**: Fetches classic and weekend stock data at regular intervals.
- **Robust Error Handling**: Manages API rate limits and other potential issues gracefully.
- **Secure Configuration**: Utilizes environment variables to manage sensitive information.
- **Flexible Data Access**: Provides a script to query and display stored data.
- **Formatted Output**: Displays query results in a readable tabular format.
- **Interactive Interface**: Offers an interactive menu for querying data without command-line arguments.
- **Logging**: Maintains detailed logs for monitoring and debugging.

## Prerequisites

Before setting up the project, ensure you have the following installed:

- **Python 3.10** or higher
- **PostgreSQL** database
- **Git** (optional, for cloning the repository)

## Installation

### 1. Clone the Repository

If you haven't already, clone the project repository to your local machine:

```bash
git clone https://github.com/quantify-team/dp.git
cd stock-parser
```

### 2. Create a Virtual Environment

It's recommended to use a virtual environment to manage dependencies:

```
python3 -m venv venv
```

### 3. Activate the Virtual Environment

- **Linux/macOS:**

  ```
  source venv/bin/activate
  ```

- **Windows (Command Prompt):**

  ```
  venv\Scripts\activate
  ```

### 4. Upgrade `pip`, `setuptools`, and `wheel`

Ensure your packaging tools are up-to-date:

```
pip install --upgrade pip setuptools wheel
```

### 5. Install Dependencies

Install the required Python packages using `requirements.txt`:

```
pip install -r requirements.txt
```

*If `requirements.txt` is not provided, you can install the necessary packages manually:*

```
pip install tinkoff-invest grpcio python-dotenv psycopg2-binary python-dateutil pytz tabulate
```

## Configuration

### 1. Set Up Environment Variables

The project uses environment variables to manage sensitive information securely. You can set these variables using a `.env` file or via shell profile files.

#### Option A: Using a `.env` File

1. **Create a `.env` File:**

   In the project directory, create a `.env` file:

   ```
   nano .env
   ```

2. **Add Environment Variables:**

   ```
   API_TOKEN=your_actual_api_token
   DB_HOST=localhost
   DB_NAME=quantify_moex_stocks
   DB_USER=quantify_system_account
   DB_PASSWORD=12quanti!4
   DB_PORT=5432
   ```

   *Replace the placeholder values with your actual credentials.*

3. **Secure the `.env` File:**

   ```
   chmod 600 .env
   ```

#### Option B: Using Shell Profile Files

1. **Edit Your Shell Profile:**

   Depending on your shell, edit `~/.bashrc` or `~/.bash_profile`:

   ```
   nano ~/.bashrc
   ```

2. **Add Export Statements:**

   ```
   # Tinkoff Invest API Token
   export API_TOKEN="your_actual_api_token"
   
   # PostgreSQL Database Credentials
   export DB_HOST="localhost"
   export DB_NAME="quantify_moex_stocks"
   export DB_USER="quantify_system_account"
   export DB_PASSWORD="12quanti!4"
   export DB_PORT="5432"
   ```

3. **Save and Apply Changes:**

   ```
   source ~/.bashrc
   ```

### 2. Database Setup

Ensure that your PostgreSQL database is set up with the necessary tables.

#### Example SQL Schema

```
CREATE TABLE classic_stocks (
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

CREATE TABLE weekend_stocks (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR(50),
    begin_time TIMESTAMPTZ,
    close_time TIMESTAMPTZ,
    open NUMERIC(12, 6),
    high NUMERIC(12, 6),
    low NUMERIC(12, 6),
    close NUMERIC(12, 6),
    UNIQUE (ticker, begin_time)
);
```

*Execute the above SQL commands in your PostgreSQL database to create the required tables.*

## Usage

### Running the Stock Parser

The `stock_parser.py` script fetches stock data and stores it in the PostgreSQL database.

#### 1. Activate the Virtual Environment

```
source venv/bin/activate
```

#### 2. Run the Script Manually (For Testing)

```
python3 stock_parser.py
```

#### 3. Run the Script in the Background Using `nohup`

```
nohup python3 stock_parser.py > stock_parser_output.log 2>&1 &
```

- Explanation:
  - **`nohup`**: Runs the command immune to hangups.
  - **`>`**: Redirects standard output to `stock_parser_output.log`.
  - **`2>&1`**: Redirects standard error to the same log file.
  - **`&`**: Runs the process in the background.

#### 4. Monitor the Logs

```
tail -f stock_parser_output.log
tail -f stock_parser_error.log
```

### Querying the Database

The `query_data.py` script allows you to query and display stored stock data.

#### 1. Ensure Environment Variables Are Set

If you're using a `.env` file, make sure it's loaded. Otherwise, ensure environment variables are exported.

#### 2. Install Additional Dependency for Query Script

The `query_data.py` script uses the `tabulate` library for formatted output. Ensure it's installed:

```
pip install tabulate
```

#### 3. Run the Query Script

- **Using Command-Line Arguments:**

  ```
  python3 query_data.py --table classic_stocks --limit 5 --ticker AAPL --start_date 2024-01-01 --end_date 2024-12-31
  ```

  **Arguments:**

  - `-t`, `--table`: Specify the table to query (`classic_stocks` or `weekend_stocks`).
  - `-l`, `--limit`: Number of records to fetch (default: 10).
  - `-k`, `--ticker`: Filter by ticker symbol.
  - `-s`, `--start_date`: Filter records from this date (inclusive). Format: `YYYY-MM-DD`.
  - `-e`, `--end_date`: Filter records up to this date (inclusive). Format: `YYYY-MM-DD`.

- **Using Interactive Menu:**

  Simply run the script without arguments:

  ```
  python3 query_data.py
  ```

  You will be presented with an interactive menu to input your query preferences.

#### 4. Example Output

```
=== Stock Data Query Menu ===
1. Query Classic Stocks
2. Query Weekend Stocks
3. Exit
Enter your choice (1-3): 1
Enter the number of records to fetch (default 10): 5
Enter ticker symbol to filter (leave blank for no filter): AAPL
Enter start date (YYYY-MM-DD) to filter (leave blank for no filter): 2024-01-01
Enter end date (YYYY-MM-DD) to filter (leave blank for no filter): 2024-12-31
+----+---------+---------------------+---------------------+--------+--------+--------+--------+
| id | ticker  | begin_time          | close_time          |   open |   high |    low |  close |
|----+---------+---------------------+---------------------+--------+--------+--------+--------|
|  1 | AAPL    | 2024-10-16 10:00:00 | 2024-10-16 10:10:00 |  150.5 |  155.0 | 149.0 | 154.5 |
|  2 | AAPL    | 2024-10-16 09:50:00 | 2024-10-16 10:00:00 |  149.0 |  151.0 | 148.0 | 150.0 |
|  3 | AAPL    | 2024-10-16 09:40:00 | 2024-10-16 09:50:00 |  148.5 |  149.5 | 147.0 | 149.0 |
|  4 | AAPL    | 2024-10-16 09:30:00 | 2024-10-16 09:40:00 |  147.0 |  148.0 | 146.0 | 147.5 |
|  5 | AAPL    | 2024-10-16 09:20:00 | 2024-10-16 09:30:00 |  146.5 |  147.5 | 145.0 | 146.0 |
+----+---------+---------------------+---------------------+--------+--------+--------+--------+
```

## Database Schema

### `classic_stocks` Table

| Column                | Data Type              | Description                |
| --------------------- | ---------------------- | -------------------------- |
| id                    | SERIAL                 | Primary key                |
| ticker                | VARCHAR                | Stock ticker symbol        |
| begin_time            | TIMESTAMPTZ            | Start time of the candle   |
| close_time            | TIMESTAMPTZ            | End time of the candle     |
| open                  | NUMERIC                | Opening price              |
| high                  | NUMERIC                | Highest price              |
| low                   | NUMERIC                | Lowest price               |
| close                 | NUMERIC                | Closing price              |
| **Unique Constraint** | `(ticker, begin_time)` | Prevents duplicate entries |

### `weekend_stocks` Table

| Column                | Data Type              | Description                |
| --------------------- | ---------------------- | -------------------------- |
| id                    | SERIAL                 | Primary key                |
| ticker                | VARCHAR                | Stock ticker symbol        |
| begin_time            | TIMESTAMPTZ            | Start time of the candle   |
| close_time            | TIMESTAMPTZ            | End time of the candle     |
| open                  | NUMERIC                | Opening price              |
| high                  | NUMERIC                | Highest price              |
| low                   | NUMERIC                | Lowest price               |
| close                 | NUMERIC                | Closing price              |
| **Unique Constraint** | `(ticker, begin_time)` | Prevents duplicate entries |

*Both tables include a unique constraint on the combination of `ticker` and `begin_time` to ensure data integrity.*

## Logging

The project maintains two primary log files:

- **`stock_parser.log`**: Contains detailed logs of the stock parser's operations.
- **`stock_parser_error.log`**: Contains error logs for debugging purposes.

Ensure that these files are located in a directory where the script's user has write permissions.

### Example Log Entry

```
2024-10-16 10:00:00,000 - INFO - Starting stock_parser script.
2024-10-16 10:00:00,500 - INFO - API_TOKEN is set.
2024-10-16 10:00:01,000 - INFO - Database connection successful.
2024-10-16 10:00:01,500 - INFO - Fetching candles for AAPL from 2024-10-16T09:50:00 to 2024-10-16T10:00:00
2024-10-16 10:00:02,000 - DEBUG - Number of candles fetched for AAPL: 1
2024-10-16 10:00:02,500 - INFO - Stored candle data for AAPL in classic_stocks.
```

## Troubleshooting

### Common Issues

1. **ModuleNotFoundError: No module named 'dotenv'**

   - **Cause**: Attempting to install the incorrect package (`dotenv` instead of `python-dotenv`) or the package is not installed.

   - Solution:

     ```
     pip install python-dotenv
     ```

2. **ImportError: cannot import name 'StatusCode' from 'tinkoff.invest'**

   - **Cause**: Incorrect import statement.

   - Solution: Modify the import in `stock_parser.py`:

     ```
     from grpc import StatusCode
     ```

3. **Environment Variables Not Loaded**

   - **Cause**: Sourcing `/etc/environment` incorrectly or environment variables not set.
   - **Solution**: Use a `.env` file with `python-dotenv` or set variables via shell profiles.

4. **Database Connection Errors**

   - **Cause**: Incorrect database credentials or PostgreSQL service not running.

   - Solution

     :

     - Verify credentials in the `.env` file.

     - Ensure PostgreSQL is running:

       ```
       sudo systemctl status postgresql
       ```

5. **Permission Denied for Log Files**

   - **Cause**: The user running the script does not have write permissions to the log files.

   - Solution:

     ```
     chmod 644 stock_parser.log stock_parser_error.log
     ```

### Steps to Resolve

1. **Check Installed Packages**

   Ensure all required packages are installed:

   ```
   pip list
   ```

2. **Verify Environment Variables**

   Confirm that environment variables are set:

   ```
   echo $API_TOKEN
   echo $DB_HOST
   echo $DB_NAME
   echo $DB_USER
   echo $DB_PASSWORD
   echo $DB_PORT
   ```

3. **Review Log Files**

   Inspect `stock_parser.log` and `stock_parser_error.log` for detailed error messages.

4. **Run Scripts Manually**

   Execute the scripts manually to identify issues:

   ```
   python3 stock_parser.py
   python3 query_data.py
   ```

### Additional Tips

- **Ensure Correct Python Version**: The project requires Python 3.10 or higher.

- **Virtual Environment Activation**: Always activate your virtual environment before running scripts.

- Secure Your `.env` File: Ensure that your `.env` file is not accessible to unauthorized users.

  ```
  chmod 600 .env
  ```

- Keep Dependencies Updated: Regularly update your Python packages to benefit from security patches and improvements.

  ```
  pip install --upgrade pip setuptools wheel
  pip list --outdated
  pip install --upgrade <package_name>
  ```
