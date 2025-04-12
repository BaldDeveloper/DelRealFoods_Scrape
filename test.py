import pandas as pd
from selenium import webdriver
from selenium.common import NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import tempfile

def click_test():
    """Clicks on each product detail link on the Del Real Foods collections page."""
    try:
        # Set up the Chrome WebDriver with a unique user data directory and headless mode
        options = Options()
        user_data_dir = tempfile.mkdtemp()
        options.add_argument(f"--user-data-dir={user_data_dir}")
        options.add_argument("--headless")  # Run Chrome in headless mode

        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)

        # Open the website
        driver.get("https://delrealfoods.com/blogs/recipes")

        # Get the page title and URL
        page_title = driver.title
        page_url = driver.current_url

        # Store the page title and URL in an array
        page_info = [page_title, page_url]

        # Find all elements with the class 'item-row'
        item_rows = driver.find_elements(By.CLASS_NAME, "item-row")

        # Initialize count
        count = 0

        # Loop through each element with the class 'item-row'
        for item in item_rows:
            # Increment count
            count += 1
            # Get all anchor elements within the item
            anchors = item.find_elements(By.TAG_NAME, "a")
            anchor_urls = [anchor.get_attribute("href") for anchor in anchors]
            # Perform actions on each item
            print(f"Count: {count}, Item Text: {item.text}, Anchor URLs: {anchor_urls}")

        # Print the contents of the array
        print(f"Page Info: {page_info}")

        # Close the browser
        driver.quit()

    except Exception as e:
        print(f"Error occurred: {e}", flush=True)

# Call the function
click_test()