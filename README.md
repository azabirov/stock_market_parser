# Tinkoff Russian Stock Market Parser

## Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
  - [Running the Stock Parser](#running-the-stock-parser)
  - [Running the Hourly Stock Parser](#running-the-hourly-stock-parser)
  - [Querying the Database](#querying-the-database)
- [Database Schema](#database-schema)
- [Logging](#logging)
- [Docker Setup](#docker-setup)
- [Troubleshooting](#troubleshooting)

## Overview

The stock market parser is a Python-based application designed to fetch stock data from the [Tinkoff Invest API](https://tinkoff.github.io/investAPI/) and store it in a PostgreSQL database. The project comprises three primary scripts located in the `src` directory:

1. **`stock_parser.py`**: Continuously fetches and stores stock data.
2. **`stock_parser_hourly.py`**: Fetches and stores hourly stock data.
3. **`query_data.py`**: Allows users to query and display stored stock data.

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
git clone https://github.com/azabirov/stock_market_parser
```

### 2. Create a Virtual Environment

It's recommended to use a virtual environment to manage dependencies:

```bash
python3 -m venv venv
```

### 3. Activate the Virtual Environment

- **Linux/macOS:**

  ```bash
  source venv/bin/activate
  ```

- **Windows (Command Prompt):**

  ```cmd
  venv\Scripts\activate
  ```

### 4. Upgrade `pip`, `setuptools`, and `wheel`

Ensure your packaging tools are up-to-date:

```bash
pip install --upgrade pip setuptools wheel
```

### 5. Install Dependencies

Install the required Python packages using `requirements.txt`:

```bash
pip install -r requirements.txt
```

## Configuration

### 1. Set Up Environment Variables

The project uses environment variables to manage sensitive information securely. You can set these variables using a `.env` file or via shell profile files.

#### Option A: Using a `.env` File

1. **Create a `.env` File:**

   In the project directory, create a `.env` file:

   ```bash
   nano .env
   ```

2. **Add Environment Variables:**

   ```env
   API_TOKEN=your_actual_api_token
   DB_HOST=localhost
   DB_NAME=quantify_moex_stocks
   DB_USER=quantify_system_account
   DB_PASSWORD=12quanti!4
   DB_PORT=5432
   ```

   *Replace the placeholder values with your actual credentials.*

3. **Secure the `.env` File:**

   ```bash
   chmod 600 .env
   ```

#### Option B: Using Shell Profile Files

1. **Edit Your Shell Profile:**

   Depending on your shell, edit `~/.bashrc` or `~/.bash_profile`:

   ```bash
   nano ~/.bashrc
   ```

2. **Add Export Statements:**

   ```bash
   export API_TOKEN="your_actual_tinkoff_api_token"
   export DB_HOST="localhost"
   export DB_NAME="quantify_moex_stocks"
   export DB_USER="quantify_system_account"
   export DB_PASSWORD="12quanti!4"
   export DB_PORT="5432"
   ```

3. **Save and Apply Changes:**

   ```bash
   source ~/.bashrc
   ```

### 2. Database Setup

Ensure that your PostgreSQL database is set up with the necessary tables.

#### Example SQL Schema

```sql
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
    ticker VARCHAR(20),
    begin_time TIMESTAMPTZ,
    close_time TIMESTAMPTZ,
    open NUMERIC(12, 6),
    high NUMERIC(12, 6),
    low NUMERIC(12, 6),
    close NUMERIC(12, 6),
    UNIQUE (ticker, begin_time)
);

CREATE TABLE classic_stocks_hourly (
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

CREATE TABLE weekend_stocks_hourly (
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
```

## Usage

### Running the Stock Parser

The `stock_parser.py` script fetches stock data and stores it in the PostgreSQL database.

#### 1. Activate the Virtual Environment

```
source venv/bin/activate
```

#### 2. Run the Script Manually (For Testing)

```bash
python3 src/stock_parser.py
```

#### 3. Run the Script in the Background Using `nohup`

```bash
source venv/bin/activate
nohup python3 src/stock_parser.py &
tail -f logs/stock_parser.log
```

- Explanation:
  - **`nohup`**: Runs the command immune to hangups.
  - **`&`**: Runs the process in the background.

#### 4. Monitor the Logs

```bash
tail -f logs/stock_parser.log
tail -f logs/stock_parser_error.log
```

### Running the Hourly Stock Parser

The `stock_parser_hourly.py` script fetches hourly stock data and stores it in the PostgreSQL database. This is useful for analyzing longer-term trends with less granular data.

#### 1. Activate the Virtual Environment

```bash
source venv/bin/activate
```

#### 2. Run the Script Manually

```bash
python3 src/stock_parser_hourly.py
```

#### 3. Run the Script in the Background Using `nohup`

```bash
source venv/bin/activate
nohup python3 src/stock_parser_hourly.py &
tail -f logs/stock_parser_hourly.log
```

#### 4. Monitor the Hourly Parser Logs

```bash
tail -f logs/stock_parser_hourly.log
tail -f logs/stock_parser_hourly_error.log
```

### Querying the Database

The `query_data.py` script allows you to query and display stored stock data.

#### 1. Ensure Environment Variables Are Set

If you're using a `.env` file, make sure it's loaded. Otherwise, ensure environment variables are exported.

#### 2. Run the Query Script

- **Using Command-Line Arguments:**

  ```bash
  python3 src/query_data.py --table classic_stocks --limit 5 --ticker AAPL --start_date 2024-01-01 --end_date 2024-12-31
  ```

  **Arguments:**

  - `-t`, `--table`: Specify the table to query (`classic_stocks` or `weekend_stocks`).
  - `-l`, `--limit`: Number of records to fetch (default: 10).
  - `-k`, `--ticker`: Filter by ticker symbol.
  - `-s`, `--start_date`: Filter records from this date (inclusive). Format: `YYYY-MM-DD`.
  - `-e`, `--end_date`: Filter records up to this date (inclusive). Format: `YYYY-MM-DD`.

- **Using Interactive Menu:**

  Simply run the script without arguments:

  ```bash
  python3 src/query_data.py
  ```

  You will be presented with an interactive menu to input your query preferences.

#### 3. Example Output

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

### `classic_stocks_hourly` Table

| Column                | Data Type              | Description                |
| --------------------- | ---------------------- | -------------------------- |
| id                    | SERIAL                 | Primary key                |
| ticker                | VARCHAR                | Stock ticker symbol        |
| begin_time            | TIMESTAMPTZ            | Start time of the candle   |
| close_time            | TIMESTAMPTZ            | End time of the candle     |
| open                  | NUMERIC                | Opening price              |
| high                  | NUMERIC                | Highest price              |
| low                   | NUMERIC                | Lowest price              |
| close                 | NUMERIC                | Closing price              |
| **Unique Constraint** | `(ticker, begin_time)` | Prevents duplicate entries |

### `weekend_stocks_hourly` Table

| Column                | Data Type              | Description                |
| --------------------- | ---------------------- | -------------------------- |
| id                    | SERIAL                 | Primary key                |
| ticker                | VARCHAR                | Stock ticker symbol        |
| begin_time            | TIMESTAMPTZ            | Start time of the candle   |
| close_time            | TIMESTAMPTZ            | End time of the candle     |
| open                  | NUMERIC                | Opening price              |
| high                  | NUMERIC                | Highest price              |
| low                   | NUMERIC                | Lowest price              |
| close                 | NUMERIC                | Closing price              |
| **Unique Constraint** | `(ticker, begin_time)` | Prevents duplicate entries |

*Both tables include a unique constraint on the combination of `ticker` and `begin_time` to ensure data integrity.*

## Logging

The project maintains two primary log files:

`logs/stock_parser.log`: Contains detailed logs of the stock parser's operations.
`logs/stock_parser_error.log`: Contains error logs for debugging purposes.

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
## Docker Setup

If you prefer to use Docker, you can run the project using the provided Dockerfile and docker-compose.yml file. This method ensures consistent environments across different systems.

### Prerequisites for Docker Setup

- Docker
- Docker Compose

### Steps to Run with Docker

1. **Build and Start the Containers:**

   In the project root directory, run:

   ```bash
   docker-compose up --build
   ```

   This command will build the Docker image for the stock parser and start both the stock parser and the PostgreSQL database containers.

2. **Verify the Containers are Running:**

   In a new terminal window, you can check the status of your containers:

   ```bash
   docker-compose ps
   ```

   You should see two containers running: `stock-parser` and `stock-parser-db`.

3. **Access Logs:**

   To view the logs of the stock parser container:

   ```bash
   docker-compose logs stock-parser
   ```

   For real-time logs:

   ```bash
   docker-compose logs -f stock-parser
   ```

4. **Stop the Containers:**

   When you're done, you can stop the containers by pressing `Ctrl+C` in the terminal where you ran `docker-compose up`, or by running:

   ```bash
   docker-compose down
   ```

   in a new terminal window.

### Notes

- The stock parser container is configured to restart automatically if it crashes.
- The PostgreSQL data is persisted in a Docker volume, so your data will be preserved even if you stop and remove the containers.
- Environment variables are loaded from the `.env` file in the project root. Make sure this file is properly configured before running the containers.

By using Docker, you ensure that the application runs in a consistent environment, regardless of your local setup. This can help avoid issues related to different Python versions or system configurations.

## Troubleshooting

Ensure correct permissions and installed dependencies.

### Common Issues

1. **ModuleNotFoundError: No module named 'dotenv'**

   - **Cause**: Attempting to install the incorrect package (`dotenv` instead of `python-dotenv`) or the package is not installed.

   - Solution:

     ```
     pip install python-dotenv
     ```


2. **Environment Variables Not Loaded**

   - **Cause**: Sourcing `/etc/environment` incorrectly or environment variables not set.
   - **Solution**: Use a `.env` file with `python-dotenv` or set variables via shell profiles.

3. **Database Connection Errors**

   - **Cause**: Incorrect database credentials or PostgreSQL service not running.

   - Solution:

     - Verify credentials in the `.env` file.

     - Ensure PostgreSQL is running:

       ```
       sudo systemctl status postgresql
       ```

4. **Permission Denied for Log Files**

   - **Cause**: The user running the script does not have write permissions to the log files.

   - Solution:

     ```bash
     chmod 644 logs/stock_parser.log logs/stock_parser_error.log
     ```

### Steps to Resolve

1. **Check Installed Packages**

   Ensure all required packages are installed:

   ```bash
   pip list
   ```

2. **Verify Environment Variables**

   Confirm that environment variables are set:

   ```bash
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

   ```bash
   python3 src/stock_parser.py
   python3 src/query_data.py
   ```

### Additional Tips

- **Ensure Correct Python Version**: The project requires Python 3.10 or higher.

- **Virtual Environment Activation**: Always activate your virtual environment before running scripts.

- Secure Your `.env` File: Ensure that your `.env` file is not accessible to unauthorized users.

  ```bash
  chmod 600 .env
  ```

- Keep Dependencies Updated: Regularly update your Python packages to benefit from security patches and improvements.

  ```bash
  pip install --upgrade pip setuptools wheel
  pip list --outdated
  pip install --upgrade <package_name>
  ```
