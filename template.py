import pandas as pd
from selenium.common import NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

import tempfile
import time


def setup_driver():
    """Set up and return a Chrome WebDriver instance."""
    options = Options()
    user_data_dir = tempfile.mkdtemp()
    options.add_argument(f"--user-data-dir={user_data_dir}")
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--enable-unsafe-swiftshader")  # Add this line
    options.page_load_strategy = 'normal'
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)


def navigate_pages(driver, product_output):
    page_title = driver.title
    page_url = driver.current_url
    # Create second driver for product details
    detail_driver = setup_driver()

    while True:
        try:
            # Wait for recipe items to be present
            wait = WebDriverWait(driver, 10)
            product_items = wait.until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".grid__item.item-row"))
            )

            i = 0
            while True:
                # Refresh the product items list at the start of each iteration
                if i >= len(product_items):
                    break

                product_item = product_items[i]
                product_image = product_item.find_element(By.CSS_SELECTOR, ".featured-image.tgggg")
                parent_element = product_image.find_element(By.XPATH, "..")
                product_href = parent_element.get_attribute("href")
                product_title = product_image.get_attribute("alt")

                # Check if product_href is a full URL, if not append to base URL
                if product_href and not product_href.startswith('http'):
                    product_href = f'https://delrealfoods.com{product_href}'

                navigate_to_detail_page(driver, detail_driver, product_title, product_href, product_output)

                print(f"Processing product item {product_title} ")
                i += 1

            # Check if next button exists and is enabled
            next_buttons = driver.find_elements(By.XPATH, "//a[@class='enable-arrow' and @title='Next »']")
            if not next_buttons:
                print("No more pages to scrape.")
                break

            # Click the next button
            next_button = next_buttons[0]
            if not next_button.is_displayed() or not next_button.is_enabled():
                print("Next button is not clickable. Ending pagination.")
                break

            driver.execute_script("arguments[0].click();", next_button)
            time.sleep(4)

        except Exception as e:
            print(f"Error during pagination: {e}")
            break

    # Close the detail driver
    detail_driver.quit()


def navigate_to_detail_page(driver, detail_driver, product_title, product_href, product_output):
    detail_driver.get(product_href)
    time.sleep(4)

    try:
        # Wait for and get the product header
        wait = WebDriverWait(detail_driver, 10)
        product_header = wait.until(
            EC.presence_of_element_located((By.CLASS_NAME, "recipe-heading"))
        )
        product_header_text = product_header.text
    except Exception as e:
        print(f"Error getting description: {e}")
        product_header_text = "Not found"

    try:
        # Get the src attribute of the 3rd image tag
        image_elements = detail_driver.find_elements(By.TAG_NAME, "img")
        if len(image_elements) >= 3:
            product_image_src = image_elements[2].get_attribute("src")
        else:
            print("Less than 3 image elements found")
            product_image_src = "Not found"
    except NoSuchElementException:
        print("Image elements not found")
        product_image_src = "Not found"

    product_output.append({
        "Page Title": driver.title,
        "Page URL": driver.current_url,
        "ProductDescription (short)": product_title,
        "Product URL": product_href,
        "Description": product_header_text,
        "Product Image URL": product_image_src
    })


def save_to_excel(product_output, output_file):
    """Save the scraped data to an Excel file."""
    try:
        df = pd.DataFrame(product_output)
        df.to_excel(output_file, index=False)
        print(f"Data saved to {output_file}")
    except Exception as e:
        print(f"Error saving to Excel: {e}")


def click_allproducts_scrape():
    try:
        driver = setup_driver()
        driver.get("https://delrealfoods.com/collections/all")

        # Initialize an array to store all products
        product_output = []

        # Navigate and scrape pages
        navigate_pages(driver, product_output)
        # Save the data to an Excel file
        output_file = "C:\\all_products_scrape_output.xlsx"
        save_to_excel(product_output, output_file)

        # Close the browser
        driver.quit()

    except Exception as e:
        print(f"Error occurred: {e}")


# Call the function
click_allproducts_scrape()
