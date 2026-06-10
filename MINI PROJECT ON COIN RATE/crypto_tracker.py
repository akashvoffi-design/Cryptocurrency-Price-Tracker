# Import the time library to add delays if needed
import time
# Import the os library to check if files exist
import os
# Import the datetime class to get the current date and time
from datetime import datetime
# Import pandas to create and save data to CSV files
import pandas
# Import the main selenium web driver
from selenium import webdriver
# Import the Service class to run the Chrome driver
from selenium.webdriver.chrome.service import Service
# Import the By class to locate elements on web pages
from selenium.webdriver.common.by import By
# Import the WebDriverWait class to wait for page elements to load
from selenium.webdriver.support.ui import WebDriverWait
# Import expected conditions to specify what we are waiting for
from selenium.webdriver.support import expected_conditions as EC
# Import the ChromeDriverManager to install the Chrome driver automatically
from webdriver_manager.chrome import ChromeDriverManager

# Print a message to the terminal saying the script has started
print("Starting the Cryptocurrency Price Tracker script...")

# Create an empty list to hold the cryptocurrency data we scrape
crypto_data_list = []

# Get the current date and time to label when this data was collected
current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Set up a try-except block to handle errors so the script does not crash unexpectedly
try:
    # Print that we are configuring the browser settings
    print("Step 1: Setting up Chrome options...")
    
    # Create a ChromeOptions object to customize how Chrome runs
    chrome_options = webdriver.ChromeOptions()
    
    # Configure Chrome to run in headless mode (in the background, without opening a visible browser window)
    chrome_options.add_argument("--headless=new")
    
    # Disable GPU hardware acceleration to save resources and avoid errors in headless mode
    chrome_options.add_argument("--disable-gpu")
    
    # Disable the sandbox security layer, which is often required when running in container/headless environments
    chrome_options.add_argument("--no-sandbox")
    
    # Prevent Chrome from running out of memory by disabling the shared memory space limitation
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    # Set a custom user agent so that CoinMarketCap thinks a real human browser is visiting the page
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36")
    
    # Print that we are installing and launching the Chrome browser driver
    print("Step 2: Initializing Chrome driver (installing if necessary)...")
    
    # Install the correct Chrome driver version automatically and start the browser with our options
    driver_service = Service(ChromeDriverManager().install())
    browser = webdriver.Chrome(service=driver_service, options=chrome_options)
    
    # Print that we are navigating to the CoinMarketCap website
    print("Step 3: Navigating to CoinMarketCap...")
    
    # Open the CoinMarketCap homepage in the background browser
    browser.get("https://coinmarketcap.com/")
    
    # Print that we are waiting for the website data table to load
    print("Step 4: Waiting for the table to load dynamically...")
    
    # Set a maximum wait time of 15 seconds for elements to appear on the page
    wait_helper = WebDriverWait(browser, 15)
    
    # Wait until the main cryptocurrency table element is fully loaded and present in the HTML page
    wait_helper.until(EC.presence_of_element_located((By.CSS_SELECTOR, "table.cmc-table")))
    
    # Print that we are locating the rows inside the table
    print("Step 5: Locating cryptocurrency table rows...")
    
    # Find all table rows (tr elements) inside the table body (tbody) of the main cryptocurrency table
    table_rows = browser.find_elements(By.CSS_SELECTOR, "table.cmc-table tbody tr")
    
    # Print how many rows were found on the loaded page
    print(f"Found {len(table_rows)} table rows. Extracting top 10 coins...")
    
    # Loop through each row in the table to find the top 10 coins
    for row in table_rows:
        
        # Stop looping if we have already successfully collected data for 10 coins
        if len(crypto_data_list) == 10:
            # Break out of the loop
            break
            
        # Find all data cells (td elements) in the current row
        cells = row.find_elements(By.TAG_NAME, "td")
        
        # Check if the row contains enough cells (it must have at least 8 cells to contain the target columns)
        if len(cells) >= 8:
            
            # Extract the rank text from the second cell (index 1) and remove any extra whitespace
            rank_text = cells[1].text.strip()
            
            # Check if the rank text is a number (to skip ads, index headers, or blank rows)
            if rank_text.isdigit():
                
                # Convert the rank text to an integer
                rank_number = int(rank_text)
                
                # Check if the rank number is between 1 and 10
                if 1 <= rank_number <= 10:
                    
                    # Extract the text from the third cell (index 2) which contains the coin name and symbol
                    name_cell_text = cells[2].text.strip()
                    
                    # Split the text by newline characters since name and symbol are on separate lines
                    name_parts = name_cell_text.split("\n")
                    
                    # Get the coin name (it is the first line, e.g., "Bitcoin")
                    coin_name = name_parts[0]
                    
                    # Get the coin symbol (it is the second line, e.g., "BTC")
                    coin_symbol = name_parts[1]
                    
                    # Extract the price text from the fourth cell (index 3)
                    price = cells[3].text.strip()
                    
                    # Extract the 24-hour change text from the fifth cell (index 4)
                    change_24h = cells[4].text.strip()
                    
                    # Get the raw HTML content of the 24-hour change cell to inspect the direction caret
                    change_html = cells[4].get_attribute("outerHTML")
                    
                    # Check if the HTML contains the caret-down class (indicating a price drop)
                    if "icon-Caret-down" in change_html:
                        # Add a minus sign before the percentage
                        change_24h = "-" + change_24h
                    # Check if the HTML contains the caret-up class (indicating a price rise)
                    elif "icon-Caret-up" in change_html:
                        # Add a plus sign before the percentage
                        change_24h = "+" + change_24h
                        
                    # Extract the market cap text from the eighth cell (index 7)
                    market_cap = cells[7].text.strip()
                    
                    # Create a dictionary representing the data for this single coin
                    coin_dictionary = {
                        "Rank": rank_number,
                        "Name": coin_name,
                        "Symbol": coin_symbol,
                        "Price": price,
                        "24h Change": change_24h,
                        "Market Cap": market_cap,
                        "Timestamp": current_time
                    }
                    
                    # Append the dictionary to our main list of cryptocurrencies
                    crypto_data_list.append(coin_dictionary)
                    
                    # Print progress showing which coin was extracted successfully
                    print(f"  [+] Extracted Rank {rank_number}: {coin_name} ({coin_symbol}) - {price}")
                    
# Catch any errors that happen during the scraping process to prevent the program from crashing
except Exception as error_message:
    # Print the error message to the terminal so the user knows what went wrong
    print(f"An error occurred during scraping: {error_message}")
    
# Code inside this block will run no matter what, even if an error occurred above
finally:
    # Check if the browser driver was successfully created
    if 'browser' in locals():
        # Print that we are closing the browser window
        print("Step 6: Closing the browser driver...")
        # Close the Chrome browser and free up system resources
        browser.quit()

# Check if we successfully collected any coin data
if len(crypto_data_list) > 0:
    # Print that we are saving the data to the Excel file
    print("Step 7: Saving data to Excel file...")
    
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
    print("No data was collected. Please check the website layout or connection.")

# Print that the script has finished executing
print("Script execution completed.")

# ==============================================================================
# PLAIN ENGLISH EXPLANATION OF HOW THIS CODE WORKS:
# ==============================================================================
# 1. IMPORTS SECTION:
#    We import libraries like 'time' for delays, 'os' to check if files exist,
#    'datetime' to get the current time, 'pandas' to make saving spreadsheet data easy,
#    and several 'selenium' tools to launch and control a web browser.
#
# 2. CHROMEDRIVER OPTIONS & SETUP:
#    We configure Chrome to run in "headless" mode. This means the browser runs
#    silently in the background without opening a window on your desktop, which
#    makes it faster and works on systems without a monitor. We also set a custom
#    'User-Agent' string to pretend we are a real human browsing from a regular computer
#    to prevent CoinMarketCap from blocking us.
#
# 3. OPENING THE WEB PAGE:
#    We open the Chrome browser, tell it to navigate to "https://coinmarketcap.com/",
#    and instruct Selenium to wait up to 15 seconds for the main cryptocurrency table
#    (which has the class name 'cmc-table') to finish loading and rendering on the page.
#
# 4. SCRAPING COIN DATA:
#    - We locate all the rows (<tr> tags) inside the table's body.
#    - We loop through the rows one by one. We look at the first cells of each row to
#      read the Rank.
#    - If the rank is a digit and is between 1 and 10, we proceed. This helps us
#      skip advertisements, sponsored items, or header lines.
#    - Inside cell 2, we split the text (e.g. "Bitcoin\nBTC\nBuy") by newlines to
#      get the clean name ("Bitcoin") and the symbol ("BTC").
#    - We read the price and market cap from their respective columns.
#    - To get the correct direction of the 24-hour change (whether price went up or down),
#      we inspect the HTML code of the change cell. If the HTML code has the word
#      'icon-Caret-down', we know the price went down, so we add a '-' sign. If it has
#      'icon-Caret-up', we add a '+' sign.
#    - We package all this information into a small dictionary along with the current time.
#
# 5. ERROR HANDLING & CLEANUP:
#    - The entire scraping sequence is inside a 'try-except' block. If the internet
#      disconnects or selectors fail, the script won't crash; instead, it will print
#      the error and move to the 'finally' step.
#    - In the 'finally' step, we close the background browser to free up memory on your PC.
#
# 6. SAVING TO FILE (APPENDING):
#    We convert our list of 10 coin data bundles into a table using pandas.
#    We look to see if the file 'crypto_prices.xlsx' already exists in our folder.
#    - If it does, we read the existing sheet, combine the old and new data together,
#      and write it back to the Excel file.
#    - If it does not, we create a new Excel file and save the data directly.
# ==============================================================================

