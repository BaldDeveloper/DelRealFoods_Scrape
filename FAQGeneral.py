import pandas as pd
from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import tempfile

def click_faq_general_scrape():
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
        driver.get("https://del-real-foods.myshopify.com/pages/general-faq")

        # Get the page title and URL
        page_title = driver.title
        page_url = driver.current_url

        # Initialize an array to store all print statements
        output = []

        # Find all elements with the class 'shg-box-vertical-align-wrapper'
        section_groups = driver.find_elements(By.CLASS_NAME, "shg-box-vertical-align-wrapper")

        section_groups_count = 0
        # Loop through all section groups
        while section_groups_count < len(section_groups):
            section_group = section_groups[section_groups_count]
            section_html = section_group.get_attribute('outerHTML')

            # Get the value of the element with the class 'shogun-heading-component'
            try:
                heading_element = section_group.find_element(By.CLASS_NAME, "shogun-heading-component")
                heading_text = heading_element.text
            except NoSuchElementException:
                heading_text = "Heading element not found"

            # Get all elements with the class 'shogun-accordion' within the section group
            accordions = section_group.find_elements(By.CLASS_NAME, "shogun-accordion")

            for accordion in accordions:
                accordion_question = accordion.find_element(By.CLASS_NAME, "shogun-accordion-title")
                accordion_answer_html = accordion.find_element(By.CLASS_NAME, "shg-theme-text-content").get_attribute('outerHTML')

                # Use BeautifulSoup to remove HTML tags
                soup = BeautifulSoup(accordion_answer_html, 'html.parser')
                accordion_answer = soup.get_text().replace('\n', '')

                # Store the collected data in the output array
                output.append({
                    "Page Title": page_title,
                    "Page URL": page_url,
                    "Heading": heading_text,
                    "Question": accordion_question.text,
                    "Answer": accordion_answer
                })

            # Increment the index
            section_groups_count += 1

        # Create DataFrame and save to Excel
        df = pd.DataFrame(output)
        df.to_excel('C:\\faq_general_scrape_output.xlsx', index=False)

        # Close the browser
        driver.quit()

    except Exception as e:
        print(f"Error occurred: {e}", flush=True)

# Call the function
click_faq_general_scrape()