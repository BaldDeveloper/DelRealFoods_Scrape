import pandas as pd
from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import tempfile

import pandas as pd
from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import tempfile

import pandas as pd
from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import tempfile

def click_k12_products_scrape():
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
        driver.get("https://foodservices.delrealfoods.com/k-12/products/")

        # Get the page title and URL
        page_title = driver.title
        page_url = driver.current_url

        # Initialize an array to store all print statements
        output = []

        # Find all elements with the class 'owl-item'
        carousel_items = driver.find_elements(By.CLASS_NAME, "owl-item")

        carousel_items_count = 0
        # Loop through all carousel items
        while carousel_items_count < len(carousel_items):
            carousel_item = carousel_items[carousel_items_count]
            slide_anchor = carousel_item.find_element(By.TAG_NAME, "a").get_attribute("href")

            # Store the collected data in the output array
            output.append({
                "Page Title": page_title,
                "Page URL": page_url,
                "Slide URL": slide_anchor
            })

            # Increment the index
            carousel_items_count += 1


        # Products - single-product
        # Find all elements with the class 'owl-item'
        blue_product_items = driver.find_elements(By.CLASS_NAME, "single-product")

        blue_products_item_count = 0
        # Loop through all carousel items
        while blue_products_item_count < len(blue_product_items):
            blue_product_item = blue_product_items[blue_products_item_count]
            blue_product_heading = blue_product_item.find_element(By.CLASS_NAME, "small-blue-heading")

            # Get all blue product items
            blue_product_list_items = blue_product_item.find_elements(By.TAG_NAME, "li")

            blue_list_item_count = 0
            # Loop through all carousel items
            while blue_list_item_count < len(blue_product_list_items):
                blue_product_list_item = blue_product_list_items[blue_list_item_count]

                # Store the collected data in the output array
                output.append({
                    "Page Title": page_title,
                    "Page URL": page_url,
                    "Slide URL": '',
                    "Blue Product Heading": blue_product_heading.text,
                    "Blue Product List Item": blue_product_list_item.text
                })
                # Increment the index
                blue_list_item_count += 1

            # Increment the index
            blue_products_item_count += 1



        # Print the output array
        for entry in output:
            print(entry)

        # Create DataFrame and save to Excel
        df = pd.DataFrame(output)
        #df.to_excel('C:\\k12_products_output.xlsx', index=False)

        # Close the browser
        driver.quit()

    except Exception as e:
        print(f"Error occurred: {e}", flush=True)

# Call the function
click_k12_products_scrape()