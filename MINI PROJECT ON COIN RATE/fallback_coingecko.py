# Import the requests library to send HTTP requests to the CoinGecko API
import requests
# Import urllib3 to disable SSL warning messages when we bypass SSL checks
import urllib3
# Import the os library to check if the CSV file already exists
import os
# Import the datetime class to get the current date and time
from datetime import datetime
# Import pandas to create and save data to CSV files
import pandas

# Disable SSL insecure request warnings to keep the terminal output clean and beginner-friendly
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Print a message to the terminal saying the script has started
print("Starting the CoinGecko API Fallback Price Tracker script...")

# Get the current date and time to label when this data was collected
current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Define the URL of the free CoinGecko API to fetch the top 10 coins by market cap
api_url = "https://api.coingecko.com/api/v3/coins/markets"

# Set up the parameters for the API request
api_parameters = {
    # Request the prices in US Dollars (USD)
    "vs_currency": "usd",
    # Order the results by market cap descending (highest first)
    "order": "market_cap_desc",
    # Retrieve exactly 10 coins
    "per_page": 10,
    # Retrieve the first page of results
    "page": 1,
    # Do not request sparkline chart data to keep the response fast and light
    "sparkline": "false"
}

# Define browser-like headers to prevent the API from blocking our script
api_headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
}

# Create an empty list to store the formatted coin data
crypto_data_list = []

# Set up a try-except block to handle errors so the script does not crash unexpectedly
try:
    # Print that we are making the API request
    print("Step 1: Sending request to the free CoinGecko API...")
    
    # Send the GET request to the CoinGecko API with parameters, headers, and disable SSL validation (verify=False) to prevent local network SSL errors
    response = requests.get(api_url, params=api_parameters, headers=api_headers, verify=False)
    
    # Print the status of the response
    print(f"Step 2: Received response status code {response.status_code}")
    
    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        
        # Parse the JSON response from the API into a Python list of dictionaries
        coins_list = response.json()
        
        # Print that we are formatting the coin data
        print("Step 3: Parsing and formatting coin data...")
        
        # Loop through each coin in the list returned by the API
        for coin in coins_list:
            
            # Extract the rank of the coin from the API data
            rank = coin["market_cap_rank"]
            
            # Extract the full name of the coin (e.g., "Bitcoin")
            coin_name = coin["name"]
            
            # Extract the symbol of the coin (e.g., "BTC") and convert to uppercase
            coin_symbol = coin["symbol"].upper()
            
            # Extract the current price as a number
            price_number = coin["current_price"]
            
            # If the price is 1 dollar or more, format it with 2 decimal places and commas
            if price_number >= 1.0:
                price_string = f"${price_number:,.2f}"
            # If the price is less than 1 dollar, format it with 4 decimal places for precision
            else:
                price_string = f"${price_number:,.4f}"
                
            # Extract the 24-hour price change percentage
            change_number = coin["price_change_percentage_24h"]
            
            # Check if the change percentage is not None (some new coins may have blank change data)
            if change_number is not None:
                # If the change is positive or zero, prepend a plus sign (+)
                if change_number >= 0:
                    change_string = f"+{change_number:.2f}%"
                # If the change is negative, it will already have a minus sign (-), so format as is
                else:
                    change_string = f"{change_number:.2f}%"
            # If the change data is missing, label it as "0.00%"
            else:
                change_string = "0.00%"
                
            # Extract the market cap number
            mcap_number = coin["market_cap"]
            
            # If market cap is in trillions (greater than or equal to 1,000,000,000,000)
            if mcap_number >= 1_000_000_000_000:
                # Divide by 1 trillion and add 'T'
                mcap_string = f"${mcap_number / 1_000_000_000_000:.2f}T"
            # If market cap is in billions (greater than or equal to 1,000,000,000)
            elif mcap_number >= 1_000_000_000:
                # Divide by 1 billion and add 'B'
                mcap_string = f"${mcap_number / 1_000_000_000:.2f}B"
            # If market cap is in millions (greater than or equal to 1,000,000)
            elif mcap_number >= 1_000_000:
                # Divide by 1 million and add 'M'
                mcap_string = f"${mcap_number / 1_000_000:.2f}M"
            # Otherwise, just show the exact number with commas
            else:
                mcap_string = f"${mcap_number:,}"
                
            # Create a dictionary representing the data for this single coin
            coin_dictionary = {
                "Rank": rank,
                "Name": coin_name,
                "Symbol": coin_symbol,
                "Price": price_string,
                "24h Change": change_string,
                "Market Cap": mcap_string,
                "Timestamp": current_time
            }
            
            # Append the coin data dictionary to our main list
            crypto_data_list.append(coin_dictionary)
            
            # Print progress showing which coin was processed successfully
            print(f"  [+] Formatted Rank {rank}: {coin_name} ({coin_symbol}) - {price_string}")
            
    # If the response code was not 200, print an error message with the code
    else:
        print(f"Failed to fetch data from CoinGecko API. Server returned code: {response.status_code}")
        
# Catch any errors (like internet disconnection) that happen during the execution
except Exception as error_message:
    # Print the error details to the terminal
    print(f"An error occurred: {error_message}")

# Check if we successfully collected any coin data
if len(crypto_data_list) > 0:
    # Print that we are saving the data to the Excel file
    print("Step 4: Saving data to Excel file...")
    
    # Define the name of the Excel file where the data will be stored
    excel_file_name = "crypto_prices.xlsx"
    
    # Convert our list of coin dictionaries into a pandas DataFrame object
    new_data_frame = pandas.DataFrame(crypto_data_list)
    
    # Check if the Excel file already exists in the folder
    if os.path.exists(excel_file_name):
        # Read the existing data from the Excel file
        existing_data_frame = pandas.read_excel(excel_file_name)
        # Combine the old data and the new data together into a single table
        combined_data_frame = pandas.concat([existing_data_frame, new_data_frame], ignore_index=True)
        # Save the combined data back to the Excel file (index=False keeps it clean)
        combined_data_frame.to_excel(excel_file_name, index=False)
        # Print a success message confirming the data was appended
        print(f"Success! Appended new data to '{excel_file_name}' (Total rows added: {len(crypto_data_list)}).")
    else:
        # Save the new data directly to a new Excel file
        new_data_frame.to_excel(excel_file_name, index=False)
        # Print a success message confirming the new file was created
        print(f"Success! Created '{excel_file_name}' and saved the first batch of data.")
        
else:
    # Print a warning if no data was collected
    print("No data was collected from the API fallback.")

# Print that the script has finished executing
print("Script execution completed.")

# ==============================================================================
# PLAIN ENGLISH EXPLANATION OF HOW THIS CODE WORKS:
# ==============================================================================
# 1. IMPORTS SECTION:
#    We import libraries like 'requests' to talk to the internet, 'os' to check
#    if files exist, 'datetime' to get the current time, and 'pandas' to make
#    saving our spreadsheet data easy.
#
# 2. CONFIGURATION:
#    We set up the Web URL for CoinGecko's public database and define the details
#    we want to ask for (prices in USD, sorted by size, top 10 results, no extra charts).
#    We also add a 'User-Agent' header so the CoinGecko server knows we are a safe
#    requesting client and doesn't block us.
#
# 3. REQUESTING DATA:
#    The script sends an HTTP GET request to CoinGecko. If the connection works,
#    the server returns a status code of 200 and a JSON-formatted list of coins.
#
# 4. PROCESSING AND FORMATTING COINS:
#    We loop through the 10 coins returned. For each coin, we extract its details:
#    - We format prices with commas and two decimals (or four decimals if tiny).
#    - We format the percentage change with a '+' or '-' sign.
#    - We format the large market cap numbers into clean values like '$1.22T' (Trillion)
#      or '$195.87B' (Billion) to make them readable.
#    - We bundle these details together in a dictionary along with the current time.
#
# 5. SAVING TO FILE:
#    We convert the list of coin bundles into a table structure using pandas.
#    If the 'crypto_prices.xlsx' spreadsheet already exists, we open it, combine the old
#    and new data together, and save it back to the Excel file. If it doesn't exist,
#    we create a new Excel file and save the data.
# ==============================================================================
