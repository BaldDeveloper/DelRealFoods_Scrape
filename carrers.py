from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

def scrape_title_and_header():
    # Set up the Chrome WebDriver with headless mode
    options = Options()
    #options.add_argument("--headless")  # Run Chrome in headless mode

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    try:
        # Open the website
        driver.get("https://delrealfoods.com/pages/careers")

        # Get the title of the page
        title = driver.title
        print("Page Title:", title)

        # Get the value of the element with the class 'career-header'
        career_header = driver.find_element(By.CLASS_NAME, "career-header").text
        print("Career Header:", career_header)

    except Exception as e:
        print(f"Error occurred: {e}")

    finally:
        # Close the browser
        driver.quit()

# Call the function
scrape_title_and_header()