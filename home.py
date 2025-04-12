from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
import tempfile


def click_home_scrape():
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
        driver.get("https://delrealfoods.com/")

        # Get all single page items here
        # get the wide-banner-type-5-block class div
        # get the h2 and p elements within it
        # get the href attribute of all anchor elements within it


        # Find all elements with the class 'slider_style_2'
        slider_items = driver.find_elements(By.CLASS_NAME, "slider_style_2")

        slider_items_count = 0
        # Loop through all slider images and grab the URL
        while slider_items_count < len(slider_items):
            slider_item = slider_items[slider_items_count]

            # Get the value of the data-slick-index attribute
            data_slick_index = slider_item.get_attribute("data-slick-index")
            print(f"Slider Item {slider_items_count}: data-slick-index = {data_slick_index}")

            # Get all anchor elements within the slider item
            anchors = slider_item.find_elements(By.TAG_NAME, "a")
            for anchor in anchors:
                href = anchor.get_attribute("href")
                print(f"Anchor href: {href}")

            # Get all image elements within the slider item
            images = slider_item.find_elements(By.TAG_NAME, "img")
            for img in images:
                src = img.get_attribute("src")
                print(f"Image src: {src}")


            # Add code to add all of the hrefs and srcs to a list

            # Increment the index only after re-locating the list
            slider_items_count += 1





        # get all banner-images
        # loop through each banner image and get the anchor href and image src attributes

        # Close the browser
        driver.quit()

    except Exception as e:
        print(f"Error occurred: {e}", flush=True)

# Call the function
click_home_scrape()
