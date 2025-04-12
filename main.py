from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
import tempfile


def click_product_details():
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

        # Find all elements with the class 'product-detail'
        product_items = driver.find_elements(By.CLASS_NAME, "item-row")

        i = 0
        while i < len(product_items):
            item = product_items[i]
            title = item.find_element(By.CLASS_NAME, "grid-link__title")
            link = item.find_element(By.CLASS_NAME, "grid-link")
            print(str(i) + ": " + driver.title + " - " + title.text, flush=True)

            if title:
                ActionChains(driver).move_to_element(link).click(link).perform()

                # Wait for the new page to load
                # Uncomment and adjust the wait condition as needed
                # WebDriverWait(driver, 10).until(
                #     EC.presence_of_element_located((By.XPATH, '//*[@id="desc_pro"]/div[1]'))
                # )

                # Go back to the previous page
                driver.back()

                # Re-locate the product items after navigating back
                product_items = driver.find_elements(By.CLASS_NAME, "item-row")

            # Increment the index only after re-locating the list
            i += 1

        # Close the browser
        driver.quit()

    except Exception as e:
        print(f"Error occurred: {e}", flush=True)

# Call the function
click_product_details()