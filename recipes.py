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

"""Complete."""

def setup_driver():
    """Set up and return a Chrome WebDriver instance."""
    options = Options()
    user_data_dir = tempfile.mkdtemp()
    options.add_argument(f"--user-data-dir={user_data_dir}")
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.page_load_strategy = 'normal'
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)


def scrape_product_details(driver, product_element, page_title, page_url, product_output):
    """
    Extract details of a single recipe product from its preview card.
    Only processes specific allowed recipes defined in allowed_titles.
    Extracts:
    - Image URL
    - Product title
    - Product URL
    - Review badge
    Then navigates to product page for additional details.
    """
    try:
        article_image = product_element.find_element(By.CLASS_NAME, "article-image")
        article_img = article_image.find_element(By.TAG_NAME, "img")
        article_img_url = article_img.get_attribute("src")

        article_content = product_element.find_element(By.CLASS_NAME, "article-content")
        article_anchor = article_content.find_element(By.TAG_NAME, "a")
        article_anchor_url = article_anchor.get_attribute("href")
        article_anchor_text = article_anchor.text

        # List of allowed article_anchor_text values
        allowed_titles = [
            "Shredded Beef Crepes"
        ]

        # Process only if the article_anchor_text is in the allowed list
        if article_anchor_text not in allowed_titles:
            print(f"Skipping product: {article_anchor_text}")
            return

        if article_anchor_url.startswith("/"):
            base_url = "https://delrealfoods.com"
            article_anchor_url = base_url + article_anchor_url

        try:
            article_review_badge = product_element.find_element(By.CLASS_NAME, "stamped-badge")
            article_review = article_review_badge.get_attribute("aria-label")
        except NoSuchElementException:
            article_review = "No review"

        driver.get(article_anchor_url)
        time.sleep(8)

        ap_data = scrape_additional_data(driver,article_anchor_text)

        # Create base product data
        base_data = {
            "Page Title": page_title,
            "Page URL": page_url,
            "Product Header": article_anchor_text,
            "Product Review": article_review,
            "Product Image URL": article_img_url,
            "Product Anchor URL": article_anchor_url
        }

        # If ap_data is empty, append just the base data
        if not ap_data:
            product_output.append(base_data)
        else:
            # Merge base_data with ap_data and append
            base_data.update(ap_data)
            product_output.append(base_data)

        print(f"Scraped data from {article_anchor_text}")

        driver.back()
        time.sleep(2)

    except Exception as e:
        print(f"Error scraping product details: {e}")


def scrape_additional_data(driver,article_anchor_text):
    """
    Extract detailed recipe information from individual recipe pages.
    Scrapes:
    - Recipe heading
    - Description
    - Ingredients header and list
    - Preparation header and steps
    - PDF recipe URL
    Returns data as dictionary.
    """
    ap_data = {}

    # Get product item heading
    try:
        heading_elements = driver.find_elements(By.CLASS_NAME, "vc_custom_heading")
        if len(heading_elements) >= 1:
            product_item_heading = heading_elements[1].text
            ap_data["Product Item Heading"] = product_item_heading
    except NoSuchElementException:
        print("Product item heading not found")

    # Get product item description
    if article_anchor_text == "Shredded Beef Crepes":
        description_xpath = "//*[@id='shopify-section-recipe-article']/div[1]/div/article/div/section/div/div[2]/*/*/*/p"
    else:
        description_xpath = "//*[@id='shopify-section-recipe-article']/div[1]/div/article/div/section/div/div[2]/*/*/*/*/*/p"


    try:
        product_item_description = driver.find_element(By.XPATH, description_xpath).text
        ap_data["Product Item Description"] = product_item_description
    except NoSuchElementException:
        try:
            description_xpath = "//*[@id='shopify-section-recipe-article']/div[1]/div/article/div/section/div/div[2]/div/div/div[2]/p"
            product_item_description = driver.find_element(By.XPATH, description_xpath).text
            ap_data["Product Item Description"] = product_item_description
        except NoSuchElementException:
            print("Product item description not found")

    # Get product item ingredients heading
    try:
        heading_elements = driver.find_elements(By.CLASS_NAME, "vc_custom_heading")
        if len(heading_elements) >= 2:
            product_item_ingredients = heading_elements[1].text
            ap_data["Ingredients Header"] = product_item_ingredients
    except NoSuchElementException:
        print("Product item ingredients not found")

    # Get product item ingredients list
    try:
        ingredients_ul = driver.find_element(By.CLASS_NAME, "dt-sc-fancy-list")
        product_item_ingredient_list = [li.text for li in ingredients_ul.find_elements(By.TAG_NAME, "li")]
        ap_data["Product Item Ingredient List"] = product_item_ingredient_list
    except NoSuchElementException:
        print("Product item ingredient list not found")

    # Get product item preparation heading
    try:
        heading_elements = driver.find_elements(By.CLASS_NAME, "vc_custom_heading")
        if len(heading_elements) >= 3:
            product_item_preparation = heading_elements[2].text
            ap_data["Product Item Preparation"] = product_item_preparation

    except NoSuchElementException:
        print("Product item preparation not found")

    # Get product item preparation list
    try:
        preparation_elements = driver.find_elements(By.CSS_SELECTOR, ".wpb_text_column.wpb_content_element")
        if len(preparation_elements) >= 2:
            product_item_preparation_list = preparation_elements[1].text
            ap_data["Product Item Preparation List"] = product_item_preparation_list
        else:
            product_item_preparation_list = preparation_elements[0].text
            ap_data["Product Item Preparation List"] = product_item_preparation_list
    except NoSuchElementException:
        print("Product item preparation list not found")

    # Get recipe PDF URL
    try:
        product_recipe_pdf_url = driver.find_element(By.CSS_SELECTOR, "a.pdf-print").get_attribute("href")
        ap_data["Product Recipe PDF URL"] = product_recipe_pdf_url
    except NoSuchElementException:
        print("Product recipe PDF URL not found")

    return ap_data


def navigate_pages(driver, product_output):
    """
    Navigate through recipe listing pages using pagination.
    For each page:
    - Waits for recipe items to load
    - Scrapes details of each recipe
    - Clicks next page button if available
    - Handles stale elements by retrying
    """
    page_title = driver.title
    page_url = driver.current_url

    while True:
        try:
            # Wait for recipe items to be present
            wait = WebDriverWait(driver, 10)
            recipe_items = wait.until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".cust-blog.grid__item"))
            )

            i = 0
            while i < len(recipe_items):
                try:
                    recipe_item = recipe_items[i]
                    article_content = recipe_item.find_element(By.CLASS_NAME, "article")
                    scrape_product_details(driver, article_content, page_title, page_url, product_output)

                    # Refresh the recipe_items list
                    recipe_items = driver.find_elements(By.CSS_SELECTOR, ".cust-blog.grid__item")
                except StaleElementReferenceException:
                    print("Stale element encountered. Re-locating the element.")
                    continue
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


def save_to_excel(product_output, output_file):
    """Save scraped recipe data to Excel file at specified output path."""
    try:
        df = pd.DataFrame(product_output)
        df.to_excel(output_file, index=False)
        print(f"Data saved to {output_file}")
    except Exception as e:
        print(f"Error saving to Excel: {e}")


def click_recipes_scrape():
    """
    Main execution function that:
    - Initializes Chrome WebDriver
    - Starts scraping from recipes page
    - Collects all recipe data
    - Saves results to Excel
    - Cleans up browser instance
    """
    try:
        driver = setup_driver()
        driver.get("https://delrealfoods.com/blogs/recipes")

        # Initialize an array to store all products
        product_output = []

        # Navigate and scrape pages
        navigate_pages(driver, product_output)

        # Save the data to an Excel file
        output_file = "C:\\recipes_scrape_output.xlsx"
        save_to_excel(product_output, output_file)

        # Close the browser
        driver.quit()

    except Exception as e:
        print(f"Error occurred: {e}")


# Call the function
click_recipes_scrape()
