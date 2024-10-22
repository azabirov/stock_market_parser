# Use the official Python image from Docker Hub
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file to the working directory
COPY requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire src directory to the working directory
COPY src/ ./src/

# Make the wait-for-it.sh script executable
RUN chmod +x ./src/wait-for-it.sh

# Set environment variables (if any defaults are needed)
# ENV VARIABLE_NAME=default_value

# Expose any ports if necessary (not required for our scripts)
# EXPOSE 8000

# Set the command to run the stock_parser.py script using wait-for-it.sh
CMD ["./src/wait-for-it.sh", "db:5432", "--", "python", "src/stock_parser.py"]
