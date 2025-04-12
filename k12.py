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

def click_k12_scrape():
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
        driver.get("https://foodservices.delrealfoods.com/")

        # Get the page title and URL
        page_title = driver.title
        page_url = driver.current_url

        # Initialize an array to store all print statements
        output = []

        # Find all elements with the class 'item-home'
        slides = driver.find_elements(By.CLASS_NAME, "item-home")

        slides_count = 0
        # Loop through all slides
        while slides_count < len(slides):
            slide = slides[slides_count]
            slide_anchor = slide.find_element(By.TAG_NAME, "a").get_attribute("href")

            # Store the collected data in the output array
            output.append({
                "Page Title": page_title,
                "Page URL": page_url,
                "Slide URL": slide_anchor
            })

            # Increment the index
            slides_count += 1


        # Find all elements with the class 'item-home'
        columns = driver.find_elements(By.CLASS_NAME, "column-content")

        columns_count = 0
        # Loop through all columns
        while columns_count < len(columns):
            column = columns[columns_count]
            column_anchor = column.find_element(By.TAG_NAME, "a").get_attribute("href")

            # Store the collected data in the output array
            output.append({
                "Page Title": page_title,
                "Page URL": page_url,
                "Slide URL": slide_anchor,
                "Column URL": column_anchor
            })

            # Increment the index
            columns_count += 1

        # Print the output array
        for entry in output:
            print(entry)

        # Create DataFrame and save to Excel
        df = pd.DataFrame(output)
        df.to_excel('C:\\k12_scrape_output.xlsx', index=False)

        # Close the browser
        driver.quit()

    except Exception as e:
        print(f"Error occurred: {e}", flush=True)

# Call the function
click_k12_scrape()