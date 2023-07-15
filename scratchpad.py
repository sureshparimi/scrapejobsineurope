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

def copy_data(source_file, destination_file):
    with open(source_file, 'r') as source:
        source_data = json.load(source)
    
    with open(destination_file, 'r') as destination:
        destination_data = json.load(destination)
    
    destination_data.extend(source_data)
    
    with open(destination_file, 'w') as destination:
        json.dump(destination_data, destination, indent=4)

source_file = 'ottacomdata.json'
destination_file = 'masterdatabase.json'

# Append preexisting content from ottacomdata.json to masterdatabase.json
copy_data(source_file, destination_file)

def remove_duplicates(input_file, output_file):
    with open(input_file, 'r') as file:
        data = json.load(file)

    unique_joblinks = set()
    unique_records = []
    removed_records = []

    for job in data:
        joblink = job['JobLink']
        if joblink not in unique_joblinks:
            unique_joblinks.add(joblink)
            unique_records.append(job)
        else:
            removed_records.append(job)

    with open(output_file, 'w') as file:
        json.dump(unique_records, file, indent=4)

    with open("removed_duplicate_records.json", 'w') as removed_file:
        json.dump(removed_records, removed_file, indent=4)

    print("Removed Duplicate Records:")
    for removed_record in removed_records:
        print(removed_record)

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
    Locators.NEWLY_ADDED,
    Locators.FULLY_REMOTE,
    Locators.RECENTLY_FUNDED,
    Locators.FIN_TECH_COMPANIES,
    Locators.JOBS_WITH_SALARIES,
    Locators.APPLY_VIA_OTTA,
    Locators.ALL_MATCHES,
]

# Iterate through the list of job data cards and click on each element
for job_data_card in job_data_cards:
    print("############ Scraping jobs for job card:", job_data_card, "###############################")
    try:
        job_data_card_link = driver.find_element(By.XPATH, job_data_card)
        job_data_card_link.click()
        time.sleep(5) # Add a small delay between each action
        # Add a small delay before closing the modal window
        try:
            MODAL_REMOVE_BUTTON = driver.find_element(By.XPATH,Locators.MODAL_REMOVE_BUTTON)
            if MODAL_REMOVE_BUTTON:
                MODAL_REMOVE_BUTTON.click()
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
                # driver.refresh()
                time.sleep(1)
                # Locate the Apply button
                element = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//button[@data-testid="apply-button"]/descendant::p[text()="Apply"]')))
                element.click()
                print("this is after the click of Apply button")
                time.sleep(3)

                try:
                    Apply_content_job_link_element = driver.find_element(By.XPATH, Locators.apply_content_job_link)
                    JobLink = Apply_content_job_link_element.get_attribute('href')
                except:
                    try:
                        Apply_via_otta_link_element = driver.find_element(By.XPATH, '//*[@data-testid="apply-content"]//a')
                        JobLink = Apply_via_otta_link_element.get_attribute('href')
                    except:
                        try:
                            dialog_close_button_element = driver.find_element(By.XPATH, Locators.dialog_close_button)
                            dialog_close_button_element.click()
                        except:
                            pass

                        # Get the job title and link from the <h2> element
                        job_title_element = driver.find_element(By.XPATH, Locators.job_title)
                        job_link_element = job_title_element.find_element(By.TAG_NAME, 'a')
                        JobLink = job_link_element.get_attribute('href')

                        # Set the focus on the main page
                        driver.switch_to.default_content()

                    # Append job_title, job_location_text, and JobLink to ottacomdata.json file
                    job_data_list = []
                    with open('ottacomdata.json', 'a+') as json_file:
                        json_file.seek(0)
                        file_content = json_file.read()
                        if file_content:
                            job_data_list = json.loads(file_content)

                        job_data = {
                            "job_title": job_title_text,
                            "job_location": job_location_text,
                            "JobLink": JobLink
                        }
                        job_data_list.append(job_data)

                        json_file.seek(0)
                        json_file.truncate(0)
                        json.dump(job_data_list, json_file, indent=4)

                try:
                    dialog_close_button_element = driver.find_element(By.XPATH, Locators.dialog_close_button)
                    dialog_close_button_element.click()
                except:
                    pass

                WebDriverWait(driver,3)
                next_button = driver.find_element(By.XPATH, Locators.next_button_xpath)
                next_button.click()
                time.sleep(5)
                try:
                    element = driver.find_element(By.XPATH, '//h1[contains(text(), "Great progress!")]')
                    if element.is_displayed():
                        click_element(driver, Locators.HOME_BUTTON)
                    else:
                        pass
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
# input("Press any key to close the browser...")

# Close the browser
driver.quit()

# Append preexisting content from ottacomdata.json to masterdatabase.json
with open('ottacomdata.json') as ottacom_file:
    ottacom_data = json.load(ottacom_file)

with open('masterdatabase.json', 'a') as master_file:
    json.dump(ottacom_data, master_file, indent=4)

# Call remove_duplicates() function
input_file = 'masterdatabase.json'
output_file = 'UniqueJobsdataMasterFile.json'
remove_duplicates(input_file, output_file)
