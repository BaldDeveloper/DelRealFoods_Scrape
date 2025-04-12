from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
import tempfile


def click_allproducts_scrape():
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
        driver.get("https://delrealfoods.com/collections/all")

        # Find all elements with the class 'item-row'
        item_rows = driver.find_elements(By.CLASS_NAME, "item-row")

        # Loop through all elements with the class 'item-row'
        item_row_count = 0
        # Loop through all slider images and grab the URL
        while item_row_count < len(item_rows):
            item_row = item_rows[item_row_count]

            # Perform actions on each item_row element
            print(item_row_count, item_row.text)

            # Increment the index only after re-locating the list
            item_row_count += 1

        # Close the browser
        driver.quit()

    except Exception as e:
        print(f"Error occurred: {e}", flush=True)

# Call the function
click_allproducts_scrape()
