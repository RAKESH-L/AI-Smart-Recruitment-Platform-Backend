from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys # Import Keys for backspace functionality
import time
import pickle
import os

class LinkedInService:
    def __init__(self):
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        self.cookies_file = 'linkedin_cookies.pkl'

    def login(self):
        self.driver.get('https://www.linkedin.com/login')
        time.sleep(2)

        # Check if cookies file exists
        if os.path.exists(self.cookies_file):
            # Load cookies
            with open(self.cookies_file, 'rb') as cookiesfile:
                cookies = pickle.load(cookiesfile)
                for cookie in cookies:
                    self.driver.add_cookie(cookie)
            self.driver.refresh()
        else:
            # Wait for the user to log in manually
            while "feed" not in self.driver.current_url:
                time.sleep(2)

            # Save cookies
            with open(self.cookies_file, 'wb') as cookiesfile:
                pickle.dump(self.driver.get_cookies(), cookiesfile)

    def post_job(self, job_title, job_description, job_location, skills):
        try:
            self.login()
            self.driver.get('https://www.linkedin.com/job-posting/form/description/?isOneStepJobPost=true&jobId=4064789503&jobPostingFlowTrackingId=odogqssxSyu0pX6dbSV7GA%3D%3D&optInDraftWithAI=false&trk=flagship3_job_home')
            print("Navigated to job posting form.")

            # Wait and fill out job title
            title_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, 'job-title-typeahead-input-ember29'))
            )
            title_input.clear()
            title_input.send_keys(job_title)
            print("Job title entered.")
            time.sleep(2)


            # Wait and fill out the location
            location_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, 'location-typeahead-input-ember46'))
            )
            
            location_input.click()  # Ensure the input field is clicked
            location_input.send_keys(Keys.CONTROL + "a")  # Select all text
            location_input.send_keys(Keys.BACKSPACE)  # Clear the text

            location_input.send_keys(job_location)  # Now, enter the new job location
            print("Location entered.")
            time.sleep(2)
            
             # Wait for the suggestions dropdown to appear and select the first suggestion
            first_option = WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.XPATH, '//ul[@id="ember51-a11y"]/li[1]'))  # Adjust the ID if needed
            )
            
            first_option.click()  # Click the first suggestion
            print("Selected the first location from the dropdown.")
            time.sleep(2)


            # Scroll down to the job description field
            description_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, 'job-description-ember61'))
            )
            self.driver.execute_script("arguments[0].scrollIntoView(true);", description_input)
            
            # Focusing the contenteditable div before entering the description
            self.driver.execute_script("arguments[0].focus();", description_input)

            # Clear and set the job description using JavaScript
            self.driver.execute_script("arguments[0] = arguments[1];", description_input, job_description)
            print("Job description entered.")
            time.sleep(2)
            
            # Removing all skills
            skills_list = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'job-posting-shared-job-skill-typeahead__skills-list'))
            )
            
            # Find all skill buttons in the list
            skill_buttons = skills_list.find_elements(By.TAG_NAME, 'button')
            
            # Click each remove skill button
            for skill_button in skill_buttons:
                skill_button.click()
                time.sleep(1)  # Optional: Small delay to ensure smooth removal, adjust as needed

            print("All skills cleared.")

            # Wait for the 'Next' button to be clickable
            next_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[span[text()='Next']]"))
            )
            self.driver.execute_script("arguments[0].scrollIntoView(true);", next_button)

            try:
                next_button.click()
                time.sleep(3)  # Adjust the wait time as necessary
            except Exception as e:
                print(f"Failed to click 'Next' button: {e}")

            print("3rd stage")
            time.sleep(3)
            
            # Scroll and click the 'Continue' button
            continue_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[span[text()='Continue']]"))
            )
            self.driver.execute_script("arguments[0].scrollIntoView(true);", continue_button)
            time.sleep(1)  # Optional delay after scrolling

            continue_button.click()
            print("Clicked the 'Continue' button.")
            time.sleep(3)  # Adjust wait time as necessary
            
            # Scroll down and click on 'Post without promoting'
            post_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[span[text()='Post without promoting']]"))
            )

            self.driver.execute_script("arguments[0].scrollIntoView(true);", post_button)
            time.sleep(1)  # Optional: Wait for a moment after scrolling

            post_button.click()
            print("Clicked the 'Post without promoting' button.")
            time.sleep(3)  # Adjust wait time as necessary
            
            
            print("Job posted successfully.")
            
            # Optionally, wait for a confirmation message here (if applicable)

            return True

        except Exception as e:
            print(f"An error occurred during job posting: {e}")
            return False

        finally:
            self.driver.quit()