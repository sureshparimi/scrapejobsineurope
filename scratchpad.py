import json
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from locators import Locators

# Set up Chrome options
options = Options()
options.add_argument("start-maximized")
options.add_argument("disable-infobars")
options.add_argument("--disable-extensions")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--no-sandbox")
options.add_argument('--headless')
options.binary_location = "/usr/bin/chromium-browser"

# Set up Chrome options
options = Options()
options.add_argument("start-maximized")
options.add_argument("disable-infobars")
options.add_argument("--disable-extensions")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--no-sandbox")
options.add_argument('--headless')
options.binary_location = "/usr/bin/chromium-browser"

# # Set up Chrome driver service
# service = Service(ChromeDriverManager().install())

# Set up Chrome driver
driver = webdriver.Chrome(options=options)

# Maximize the browser window
driver.maximize_window()

# Open otta.com
driver.get('https://www.otta.com')

# Click on the login button
element = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, Locators.LOGIN_BUTTON)))
element.click()

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
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, Locators.HOME_BUTTON)))

# Click on the "Home" button
element = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, Locators.HOME_BUTTON)))
element.click()

time.sleep(5)

# Check if "See More" button exists
see_more_button = driver.find_element(By.XPATH, Locators.SEE_MORE_BUTTON) if driver.find_elements(By.XPATH, Locators.SEE_MORE_BUTTON) else None

# Perform actions based on the availability of the "See More" button
if see_more_button:
    see_more_button.click()
    time.sleep(2)

# Define a list of job data cards
job_data_cards = [
    Locators.NEWLY_ADDED,
    Locators.FULLY_REMOTE,
    Locators.RECENTLY_FUNDED,
    Locators.FIN_TECH_COMPANIES,
    Locators.JOBS_WITH_SALARIES,
    Locators.APPLY_VIA_OTTA,
    Locators.ALL_MATCHES,
]

# Create an empty list to store job data
job_data_list = []

# Iterate through the list of job data cards and click on each element
for job_data_card in job_data_cards:
    print("############ Scraping jobs for job card:", job_data_card, "###############################")
    try:
        job_data_card_link = driver.find_element(By.XPATH, job_data_card)
        job_data_card_link.click()
        time.sleep(5)

        # Check if modal window is present and close it
        try:
            modal_remove_button = driver.find_element(By.XPATH, Locators.MODAL_REMOVE_BUTTON)
            modal_remove_button.click()
        except:
            pass

        # Get all the elements matching the locator data-testid="page-progress-dot"
        page_progress_dots = driver.find_elements(By.XPATH, Locators.progress_dot_count)

        # Iterate through each element
        for dot in page_progress_dots:
            time.sleep(3)
            try:
                job_title_element = driver.find_element(By.XPATH, Locators.job_title)
                job_title_text = job_title_element.text
                job_location_element = driver.find_element(By.XPATH, Locators.job_location)
                job_location_text = job_location_element.text

                # Click on the "Apply" button
                element = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//button[@data-testid="apply-button"]/descendant::p[text()="Apply"]')))
                element.click()
                time.sleep(3)

                # Check if "Apply" content is present
                try:
                    apply_content_job_link_element = driver.find_element(By.XPATH, Locators.apply_content_job_link)
                    JobLink = apply_content_job_link_element.get_attribute('href')
                except:
                    try:
                        apply_via_otta_link_element = driver.find_element(By.XPATH, '//*[@data-testid="apply-content"]//a')
                        JobLink = apply_via_otta_link_element.get_attribute('href')
                    except:
                        try:
                            dialog_close_button_element = driver.find_element(By.XPATH, Locators.dialog_close_button)
                            dialog_close_button_element.click()
                        except:
                            pass

                        # Get the job title and link from the <h2> element
                        job_link_element = job_title_element.find_element(By.TAG_NAME, 'a')
                        JobLink = job_link_element.get_attribute('href')

                        # Set the focus on the main page
                        driver.switch_to.default_content()

                # Append job data to the list
                job_data = {
                    "job_title": job_title_text,
                    "job_location": job_location_text,
                    "JobLink": JobLink,
                    "JobPosted": datetime.now().strftime("%e %B %Y")
                }
                job_data_list.append(job_data)

                # Close the dialog if present
                try:
                    dialog_close_button_element = driver.find_element(By.XPATH, Locators.dialog_close_button)
                    dialog_close_button_element.click()
                except:
                    pass

                # Go to the next page
                next_button = driver.find_element(By.XPATH, Locators.next_button_xpath)
                next_button.click()
                time.sleep(3)

                # Check if "Great progress!" message is displayed
                try:
                    element = driver.find_element(By.XPATH, '//h1[contains(text(), "Great progress!")]')
                    if element.is_displayed():
                        element = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, Locators.HOME_BUTTON)))
                        element.click()
                except:
                    pass
            except Exception as e:
                print("Error occurred while clicking the Apply button. Skipping to the next iteration.")
                print(e)
                continue

    except Exception as e:
        print("Error occurred while clicking the job data card. Skipping to the next card.")
        print(e)
        continue

    # Click on the "Home" button
    element = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, Locators.HOME_BUTTON)))
    element.click()

    # Check if "See Less" button exists
    see_less_button = driver.find_element(By.XPATH, Locators.SEE_LESS_BUTTON) if driver.find_elements(By.XPATH, Locators.SEE_LESS_BUTTON) else None

    # Perform actions based on the availability of the "See Less" button
    if see_less_button:
        see_less_button.click()
        time.sleep(5)

    # Check if "See More" button exists
    see_more_button = driver.find_element(By.XPATH, Locators.SEE_MORE_BUTTON) if driver.find_elements(By.XPATH, Locators.SEE_MORE_BUTTON) else None

    # Perform actions based on the availability of the "See More" button
    if see_more_button:
        see_more_button.click()
        time.sleep(5)

# Close the browser
driver.quit()

# Write job data to ottacomdata.json file
with open('ottacomdata.json', 'w') as json_file:
    json.dump(job_data_list, json_file, indent=4)

# Append job data to masterdatabase.json file
with open('masterdatabase.json', 'a') as master_file:
    json.dump(job_data_list, master_file, indent=4)

# Print the job data
for job_data in job_data_list:
    print(job_data)
