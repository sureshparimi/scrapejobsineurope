import shutil
import json
import time
from datetime import date
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from locators import Locators

def click_element(driver, locator):
    element = driver.find_element(By.XPATH, locator)
    if element.is_displayed():
        actions = ActionChains(driver)
        actions.move_to_element(element).click().perform()
    else:
        print("Element is not displayed.")

# Set up Chrome options
chrome_options = Options()
# Uncomment the line below if you want to run Chrome in headless mode
# chrome_options.add_argument("--headless")

# Set up Chrome driver service
service = Service(ChromeDriverManager().install())

# Set up Chrome driver
driver = webdriver.Chrome(service=service, options=chrome_options)

# Maximize the browser window
driver.maximize_window()

# Open otta.com
driver.get('https://www.otta.com')

# Click on the login button
click_element(driver, Locators.LOGIN_BUTTON)

# Load test data from JSON file
with open('test_data.json') as json_file:
    test_data = json.load(json_file)

# Fill in the email and password fields
email_field = driver.find_element(By.ID, Locators.EMAIL_FIELD)
email_field.send_keys(test_data['email'])

password_field = driver.find_element(By.ID, Locators.PASSWORD_FIELD)
password_field.send_keys(test_data['password'])

# Submit the login form
password_field.submit()
WebDriverWait(driver, 5)

# Wait for the page to load completely
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, Locators.HOME_BUTTON)))

# Click on the "Home" button
click_element(driver, Locators.HOME_BUTTON)

time.sleep(5)

# Check if "See More" button exists
see_more_button = None
try:
    see_more_button = driver.find_element(By.XPATH, Locators.SEE_MORE_BUTTON)
except:
    pass

# Perform actions based on the availability of the "See More" button
if see_more_button:
    see_more_button.click()
    time.sleep(2)  # Add a small delay after clicking "See More" button

# Define a list of job data cards
job_data_cards = [
    Locators.JOBS_WITH_SALARIES,
    Locators.FIN_TECH_COMPANIES,
    Locators.FEMALE_FOUNDERS,
    Locators.FULLY_REMOTE,
    Locators.RECENTLY_FUNDED,
    Locators.APPLY_VIA_OTTA,
    Locators.NEWLY_ADDED,
]

# Iterate through the list of job data cards and click on each element
for job_data_card in job_data_cards:
    # Append a line indicating the new iteration
    with open('ottacomdata.json', 'a+') as json_file:
        json_file.write(f"########## Job Data Card: {job_data_card} ##########\n")

    print("############ Scraping jobs for job card:", job_data_card, "###############################")
    job_data_card_link = driver.find_element(By.XPATH, job_data_card)
    job_data_card_link.click()
    time.sleep(5) # Add a small delay between each action
    
    # Add a small delay before closing the modal window
    try:
        MODAL_REMOVE_BUTTON = driver.find_element(By.XPATH, Locators.MODAL_REMOVE_BUTTON)
        if MODAL_REMOVE_BUTTON:
            MODAL_REMOVE_BUTTON.click()
    except:
        pass
    
    # Get all the elements matching the locator data-testid="page-progress-dot"
    page_progress_dots = driver.find_elements(By.XPATH, Locators.progress_dot_count)

    # Iterate through each element
    for dot in page_progress_dots:
        time.sleep(5)
        try:
            job_title_element = driver.find_element(By.XPATH, Locators.job_title)
            job_title_text = job_title_element.text
            job_location_element = driver.find_element(By.XPATH, Locators.job_location)
            job_location_text = job_location_element.text
        except:
            print("Error occurred while retrieving job details. Skipping to the next iteration.")
            break

        try:
            # Locate the Apply button
            element = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//button[@data-testid="apply-button"]/descendant::p[text()="Apply"]')))
            element.click()
            print("This is after clicking the Apply button")
            time.sleep(5)

            # Simulate pressing the keyboard key 'A' to open a dialog
            # action_chains = ActionChains(driver)
            # action_chains.key_down(Keys.SHIFT).send_keys(chr(65)).key_up(Keys.SHIFT).perform()
            # WebDriverWait(driver, 5)
            
            try:
                Apply_content_job_link_element = driver.find_element(By.XPATH, Locators.apply_content_job_link)
                JobLink = Apply_content_job_link_element.get_attribute('href')
            except:
                Apply_via_otta_link_element = driver.find_element(By.XPATH, '//*[@data-testid="apply-content"]//a')
                JobLink = Apply_via_otta_link_element.get_attribute('href')

            # Append job_title, job_location_text, and JobLink to ottacomdata.json file
            with open('ottacomdata.json', 'a+') as json_file:
                json.dump({'job_title': job_title_text, 'job_location': job_location_text, 'JobLink': JobLink}, json_file)
                json_file.write('\n')

            dialog_close_button_element = driver.find_element(By.XPATH, Locators.dialog_close_button)
            dialog_close_button_element.click()
            WebDriverWait(driver, 3)
            next_button = driver.find_element(By.XPATH, Locators.next_button_xpath)
            next_button.click()
            time.sleep(5)
        except:
            print("Error occurred while clicking the Apply button. Skipping to the next iteration.")
            break

    # Click on the "Home" button
    click_element(driver, Locators.HOME_BUTTON)

    # Check if "See Less" button exists
    see_less_button = None
    try:
        see_less_button = driver.find_element(By.XPATH, Locators.SEE_LESS_BUTTON)
    except:
        pass

    # Perform actions based on the availability of the "See Less" button
    if see_less_button:
        see_less_button.click()
        time.sleep(5)  # Add a small delay after clicking "See Less" button

    # Check if "See More" button exists
    see_more_button = None
    try:
        see_more_button = driver.find_element(By.XPATH, Locators.SEE_MORE_BUTTON)
    except:
        pass

    # Perform actions based on the availability of the "See More" button
    if see_more_button:
        see_more_button.click()
        time.sleep(5)  # Add a small delay after clicking "See More" button

# Wait for user input before closing the browser
input("Press any key to close the browser...")

# Close the browser
driver.quit()
