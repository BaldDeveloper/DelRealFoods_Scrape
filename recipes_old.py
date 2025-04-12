import pandas as pd
from selenium import webdriver
from selenium.common import NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import tempfile

def click_recipes_scrape():
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

        # Get the page title, URL and Recipe Header
        page_title = driver.title
        page_url = driver.current_url

        # Left Title Info
        recipe_finder_header = driver.find_element(By.CLASS_NAME, "left-title")
        recipe_finder_clear_filters = recipe_finder_header.find_element(By.CLASS_NAME, "clear-me")
        recipe_finder_clear_filters_url = recipe_finder_clear_filters.get_attribute("href")

        # Initialize an array to store all products
        product_output = []

        # Start Page Loop
        while True:
            # Find all elements with the class 'products-grid-view'
            recipe_products = driver.find_elements(By.CLASS_NAME, "item-row")

            recipe_products_count = 0
            # Loop through all section groups
            while recipe_products_count < len(recipe_products):
                recipe_product = recipe_products[recipe_products_count]
                recipe_html = recipe_product.get_attribute('outerHTML')

                # Get the anchor URL and image URL
                article_image = recipe_product.find_element(By.CLASS_NAME, "article-image")
                article_img = article_image.find_element(By.TAG_NAME, "img")
                article_img_url = article_img.get_attribute("src")

                # Get the article content and anchor URL
                article_content = recipe_product.find_element(By.CLASS_NAME, "article-content")
                article_anchor = article_content.find_element(By.TAG_NAME, "a")
                article_anchor_url = article_anchor.get_attribute("href")

                # Check if the stamped-badge element exists
                try:
                    article_review_badge = recipe_product.find_element(By.CLASS_NAME, "stamped-badge")
                    article_review = article_review_badge.get_attribute("aria-label")
                except NoSuchElementException:
                    article_review = "No review"

                # Store the collected data in the output array
                product_output.append({
                    "Count": recipe_products_count,
                    "Page Title": page_title,
                    "Page URL": page_url,
                    "Recipe Page Header": recipe_finder_header.text,
                    "Recipe Clear Filters": recipe_finder_clear_filters.text,
                    "Recipe Clear Filters URL": recipe_finder_clear_filters_url,
                    "Product Header": article_anchor.text,
                    "Product Review": article_review,
                    "Product Image URL": article_img_url,
                    "Product Anchor URL": article_anchor_url
                })

                # Increment the index
                recipe_products_count += 1

            # Check if there is a next page
            try:
                next_button = driver.find_element(By.XPATH, "//a[@class='enable-arrow' and @title='Next »']")
                driver.execute_script("arguments[0].click();", next_button)
                driver.implicitly_wait(5)  # Wait for the next page to load

                # Re-locate elements after page reload
                recipe_finder_header = driver.find_element(By.CLASS_NAME, "left-title")
                recipe_finder_clear_filters = recipe_finder_header.find_element(By.CLASS_NAME, "clear-me")
                recipe_finder_clear_filters_url = recipe_finder_clear_filters.get_attribute("href")
            except (NoSuchElementException, StaleElementReferenceException):
                break  # Exit the loop if there is no next page or element is stale
        # End Page Loop

        # Print the output array
        # for entry in product_output:
        #     print(entry)

        # Create DataFrame and save to Excel
        df = pd.DataFrame(product_output)
        df.to_excel('C:\\recipes_scrape_output.xlsx', index=False)

        # Close the browser
        driver.quit()

    except Exception as e:
        print(f"Error occurred: {e}", flush=True)

# Call the function
click_recipes_scrape()