from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import tempfile


def click_product_details():
    """Clicks on each product detail link on the Del Real Foods collections page."""
    try:
        # Set up the Chrome WebDriver with a unique user data directory and headless mode
        options = Options()
        user_data_dir = tempfile.mkdtemp()
        options.add_argument(f"--user-data-dir={user_data_dir}")
        #options.add_argument("--headless")  # Run Chrome in headless mode
        div_text = ""
        titles = []
        alt_texts = []
        excerpt_blog_inner_texts = []

        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)

        # Open the website
        driver.get("https://delrealfoods.com/blogs/recipes-blog")
        i = 0
        while True:
            # Find all elements with the class 'product-detail'
            product_items = driver.find_elements(By.CLASS_NAME, "item-row")

            while i < len(product_items):
                item = product_items[i]
                meta_tag = driver.find_element(By.CSS_SELECTOR, 'meta[property="og:title"]')
                og_title = meta_tag.get_attribute("content")

                link = item.find_element(By.TAG_NAME, "a")
                img = link.find_element(By.TAG_NAME, "img")
                alt_text = img.get_attribute("alt")

                # Append values to lists
                titles.append(og_title)
                alt_texts.append(alt_text)

                if link:
                    ActionChains(driver).move_to_element(link).click(link).perform()

                    try:
                        excerpt_blog_div = driver.find_element(By.CLASS_NAME, "excerpt-blog-inner")
                        excerpt_blog_inner = excerpt_blog_div.find_element(By.TAG_NAME, "p")
                        excerpt_blog_inner_texts.append(excerpt_blog_inner.text)
                    except NoSuchElementException:
                        try:
                            excerpt_blog_divs = driver.find_elements(By.CLASS_NAME, "carina-text")

                            for div in excerpt_blog_divs:
                                div_text += div.text + "\n"  # Append each div's text with a newline

                            excerpt_blog_inner_texts.append(div_text)

                        except NoSuchElementException:
                            excerpt_blog_inner_texts.append("No excerpt found")

                    driver.back()
                    product_items = driver.find_elements(By.CLASS_NAME, "item-row")

                print(f"{i}: {og_title} - {alt_text} - {excerpt_blog_inner_texts[i]}", flush=True)
                i += 1

            # Check if there is a next page
            try:
                next_button = driver.find_element(By.CLASS_NAME, "enable-arrow")
                ActionChains(driver).move_to_element(next_button).click(next_button).perform()
            except NoSuchElementException:
                break  # Exit the loop if there is no next page

        driver.quit()

        # Create DataFrame and save to Excel
        df = pd.DataFrame({
            'Title': titles,
            'Alt Text': alt_texts,
            'div excerpt-blog-inner Text': excerpt_blog_inner_texts
        })
        #df.to_excel('C:\\recipe_data.xlsx', index=False)

    except Exception as e:
        print(f"Error occurred: {e}", flush=True)

# Call the function
click_product_details()