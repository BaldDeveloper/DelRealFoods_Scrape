import os
import pandas as pd
from selenium import webdriver
from selenium.common import NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import tempfile
import time

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

        # Initialize an array to store all products
        product_output = []

        # Start Page Loop
        while True:
            # Find all elements with the class 'item-row'
            recipe_products = driver.find_elements(By.CLASS_NAME, "item-row")

            recipe_products_count = 0
            # Loop through all section groups
            while recipe_products_count < len(recipe_products):
                try:
                    # Re-locate the product element to avoid stale references
                    recipe_products = driver.find_elements(By.CLASS_NAME, "item-row")
                    recipe_product = recipe_products[recipe_products_count]

                    # Get the anchor URL and image URL
                    article_image = recipe_product.find_element(By.CLASS_NAME, "article-image")
                    article_img = article_image.find_element(By.TAG_NAME, "img")
                    article_img_url = article_img.get_attribute("src")

                    article_content = recipe_product.find_element(By.CLASS_NAME, "article-content")
                    article_anchor = article_content.find_element(By.TAG_NAME, "a")
                    article_anchor_url = article_anchor.get_attribute("href")
                    article_anchor_text = article_anchor.text

                    print(article_anchor_text)

                    # Check if the URL is partial (starts with '/')
                    if article_anchor_url.startswith("/"):
                        base_url = "https://delrealfoods.com"  # Base URL of the website
                        article_anchor_url = base_url + article_anchor_url
                        # Update the href attribute of the article_anchor element using JavaScript
                        driver.execute_script("arguments[0].setAttribute('href', arguments[1]);", article_anchor, article_anchor_url)

                    # Check if the stamped-badge element exists
                    try:
                        article_review_badge = recipe_product.find_element(By.CLASS_NAME, "stamped-badge")
                        article_review = article_review_badge.get_attribute("aria-label")
                    except NoSuchElementException:
                        article_review = "No review"

                    # Navigate to the article page using the URL
                    driver.get(article_anchor_url)

                    # Initialize lists to store additional data
                    ap_data = []

                    # Find all elements on article page with the class 'wpb_wrapper'
                    ap_main_content = driver.find_element(By.CLASS_NAME, "vc_section")
                    ap_column_inners = ap_main_content.find_elements(By.CLASS_NAME, "vc_column-inner")
                    for ap_column_inner in ap_column_inners:

                        # Find all elements with the class 'vc_custom_heading' and grab their text
                        ap_wpb_wrappers = ap_column_inner.find_elements(By.CLASS_NAME, "wpb_wrapper")
                        for ap_wpb_wrapper in ap_wpb_wrappers:
                            ap_data.append(ap_wpb_wrapper.text)

                            # Initialize lists to store split data
                            ingredients_data = []
                            other_data = []

                            # Split ap_data based on the keyword "INGREDIENTS"
                            for data in ap_data:
                                if "INGREDIENTS" in data:
                                    parts = data.split("INGREDIENTS",
                                                       1)  # Split into two parts at the first occurrence of "INGREDIENTS"
                                    other_data.append(
                                        parts[0].strip())  # Add the part before "INGREDIENTS" to other_data
                                    ingredients_data.append(
                                        parts[1].strip())  # Add the part after "INGREDIENTS" to ingredients_data
                                else:
                                    other_data.append(
                                        data.strip())  # If "INGREDIENTS" is not found, add the data to other_data

                            # Store the collected data in the output array
                            product_output.append({
                                "Count": recipe_products_count,
                                "Page Title": page_title,
                                "Page URL": page_url,
                                "Product Header": article_anchor_text,
                                "Product Review": article_review,
                                "Product Image URL": article_img_url,
                                "Product Anchor URL": article_anchor_url,
                                "Other Data": other_data,
                                "Ingredients": ingredients_data
                            })

                        # # Find all elements with the class 'wpb_text_column' and grab their text
                        # text_column = ap_wpb_wrapper.find_element(By.CLASS_NAME, "wpb_text_column")
                        # if text_column:
                        #     ap_data.append(text_column.text)

                        # ap_list_data = []
                        # ap_list_items = driver.find_elements(By.CLASS_NAME, "dt-sc-fancy-list")
                        # for ap_list_item in ap_list_items:
                        #     ap_list_data.append(ap_list_item.text)
                        #
                        # ap_data.append(ap_list_data)

                    # Return to the previous page
                    driver.back()

                    # Wait for the page to reload
                    time.sleep(3)





                except StaleElementReferenceException:
                    # Handle stale element by re-locating the elements
                    recipe_products = driver.find_elements(By.CLASS_NAME, "item-row")
                    continue

                # Increment the index
                recipe_products_count += 1

            # Check if there is a next page
            try:
                next_button = driver.find_element(By.XPATH, "//a[@class='enable-arrow' and @title='Next »']")
                driver.execute_script("arguments[0].click();", next_button)
                time.sleep(2)  # Wait for the next page to load
            except (NoSuchElementException, StaleElementReferenceException):
                break  # Exit the loop if there is no next page or element is stale
        # End Page Loop

        # Save the DataFrame to the C:\ directory
        output_file = "C:\\recipes_scrape_output.xlsx"
        df = pd.DataFrame(product_output)
        df.to_excel(output_file, index=False)

        # Close the browser
        driver.quit()

    except Exception as e:
        print(f"Error occurred: {e}", flush=True)

# Call the function
click_recipes_scrape()