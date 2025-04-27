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


def navigate_more_buttons(driver, product_output):
    try:
        # Wait for initial page load
        wait = WebDriverWait(driver, 10)
        product_links = wait.until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "dt-sc-button"))
        )

        # Store href values and retry logic for failed URLs
        product_hrefs = [link.get_attribute("href") for link in product_links]
        failed_urls = []

        # Create a separate driver for group pages
        group_driver = setup_driver()

        try:
            for product_href in product_hrefs:
                try:
                    if not product_href:
                        continue

                    # Ensure URL is complete
                    if not product_href.startswith('http'):
                        product_href = f'https://delrealfoods.com{product_href}'

                    print(f"Processing link: {product_href}")
                    navigate_to_group_page(driver, group_driver, product_href, product_output)
                    time.sleep(4)  # Add delay between processing links

                except Exception as e:
                    print(f"Error processing link {product_href}: {e}")
                    failed_urls.append(product_href)
                    continue

            # Retry failed URLs once
            if failed_urls:
                print("Retrying failed URLs...")
                for failed_url in failed_urls:
                    try:
                        navigate_to_group_page(driver, group_driver, failed_url, product_output)
                        time.sleep(2)
                    except Exception as e:
                        print(f"Final attempt failed for {failed_url}: {e}")

        finally:
            group_driver.quit()

    except Exception as e:
        print(f"Error during pagination: {e}")


def navigate_to_group_page(driver, detail_driver, product_href, product_output):
    wait = WebDriverWait(detail_driver, 10)
    detail_driver.get(product_href)
    page_title = detail_driver.title
    page_url = detail_driver.current_url

    try:
        # Wait for product wrappers to be present and get a fresh list
        product_wrappers = wait.until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "dt-recipe-product-wrapper"))
        )

        # Store all product URLs first
        product_urls = []
        for wrapper in product_wrappers:
            try:
                thumb_anchor = wrapper.find_element(By.CLASS_NAME, "dt-recipe-product-thumb").find_element(By.TAG_NAME, "a")
                product_urls.append(thumb_anchor.get_attribute("href"))
            except NoSuchElementException:
                continue

        # Process each URL
        for product_url in product_urls:
            try:
                # Get h2 values from detail page
                ap_data = navigate_to_detail_page(detail_driver, product_url, product_output, page_title, page_url)
                print(f"Found h2 values: {ap_data}")

                # Create base product data
                base_data = {
                    "Page Title": page_title,
                    "Page URL": page_url
                }

                # Merge and append data
                if ap_data:
                    base_data.update(ap_data)
                product_output.append(base_data)

                # Go back to group page with explicit wait
                detail_driver.get(product_href)
                wait.until(EC.presence_of_element_located((By.CLASS_NAME, "dt-recipe-product-wrapper")))
                time.sleep(2)

            except Exception as e:
                print(f"Error processing product URL {product_url}: {e}")
                continue

    except Exception as e:
        print(f"Error in group page {product_href}: {e}")


def navigate_to_detail_page(driver, product_url, product_output, page_title, page_url):
    """Navigate to and scrape individual product detail pages."""
    driver.get(product_url)
    time.sleep(4)

    ap_data = {}
    pdf_urls = {}

    try:
        # Find all column containers
        columns = driver.find_elements(By.CLASS_NAME, "vc_col-sm-6")

        if len(columns) != 2:
            print(f"Expected 2 columns, found {len(columns)}")
            return ap_data

        # First column - get image URL
        try:
            image_element = columns[0].find_element(By.TAG_NAME, "img")
            image_url = image_element.get_attribute("src")
            if image_url:
                ap_data["Product Image URL"] = image_url
        except NoSuchElementException:
            print("No image found in first column")

        # Second column - get heading and buttons with their titles
        try:
            h2_element = columns[1].find_element(By.TAG_NAME, "h2")
            ap_data["Product Item Heading"] = h2_element.text

            # Find h5 elements and corresponding PDF buttons
            h5_elements = columns[1].find_elements(By.TAG_NAME, "h5")
            pdf_buttons = columns[1].find_elements(By.CSS_SELECTOR,
                ".dt-sc-button.medium.filled.dt-custom-colorfill-coverbg.pdf-print")

            # Process each button and its corresponding h5 title
            for i in range(min(len(h5_elements), len(pdf_buttons))):
                try:
                    title = h5_elements[i].text
                    pdf_url = pdf_buttons[i].get_attribute("href")
                    if pdf_url:
                        pdf_urls[title] = pdf_url
                except Exception as e:
                    print(f"Error getting PDF URL for {title}: {e}")
                    continue

            if pdf_urls:
                for title, url in pdf_urls.items():
                    ap_data[f"PDF URL - {title}"] = url

        except NoSuchElementException:
            print("No h2 or PDF buttons found in second column")

    except NoSuchElementException:
        print("No columns found on page")

    return ap_data



def save_to_excel(product_output, output_file):
    """Save the scraped data to an Excel file."""
    try:
        df = pd.DataFrame(product_output)
        df.to_excel(output_file, index=False)
        print(f"Data saved to {output_file}")
    except Exception as e:
        print(f"Error saving to Excel: {e}")


def start_scrape():
    # Food Services Page
    try:
        driver = setup_driver()
        driver.get("https://buy.delrealfoods.com/")

        # Initialize an array to store all products
        product_output = []

        # Scrape all info for Food Services page

        # Navigate using "More" buttons and scrape pages
        navigate_more_buttons(driver, product_output)
        # Save the data to an Excel file
        # output_file = "C:\\all_products_scrape_output.xlsx"
        # save_to_excel(product_output, output_file)

        # Close the browser
        driver.quit()

    except Exception as e:
        print(f"Error occurred: {e}")


# Call the function
start_scrape()
