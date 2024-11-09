'''
People
Posts
Companies
Groups
Jobs
Products
Services
Events
Courses
Schools
All filters
'''

import time
import csv
import pickle
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Constants for login and search term
USER_NAME = "kishorenand7870@protonmail.com"
PASSWORD = "Nand@321"
SEARCH_TERM = '''"Nand Kishore" + "Latest"'''

# Define flagged keywords for different violation categories
HATE_SPEECH_KEYWORDS = ["racist", "bigotry", "hate speech", "xenophobia", "discrimination", "hateful"]
SPAM_KEYWORDS = ["free", "win", "offer", "limited time", "claim your prize", "click here", "discount"]
MISINFORMATION_KEYWORDS = ["fake news", "misleading", "conspiracy theory", "false claim", "unverified"]
INAPPROPRIATE_CONTENT_KEYWORDS = ["nude", "sex", "pornography", "graphic", "violence", "abuse"]

# Configure Chrome options
options = Options()
options.add_argument("--start-maximized")
# Uncomment if incognito mode is preferred
# options.add_argument("--incognito")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Load LinkedIn login page
driver.get("https://www.linkedin.com/login")

# Load cookies if available to bypass login
try:
    with open('cookies.pkl', 'rb') as file:
        cookies = pickle.load(file)
        for cookie in cookies:
            driver.add_cookie(cookie)
    driver.refresh()  # Refresh to use loaded cookies
except FileNotFoundError:
    # Enter credentials and login if cookies are unavailable
    driver.find_element(By.ID, "username").send_keys(USER_NAME)
    driver.find_element(By.ID, "password").send_keys(PASSWORD)
    driver.find_element(By.ID, "password").send_keys(Keys.RETURN)
    # Save cookies for future use
    with open('cookies.pkl', 'wb') as file:
        pickle.dump(driver.get_cookies(), file)

# Perform a search
WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.CLASS_NAME, "search-global-typeahead__input"))
).send_keys(SEARCH_TERM, Keys.RETURN)

# Wait for search results to load
time.sleep(random.uniform(5, 10))

# Click on the "Posts" filter
filter_buttons = WebDriverWait(driver, 10).until(
    EC.presence_of_all_elements_located((By.CLASS_NAME, "search-reusables__filter-pill-button"))
)
for button in filter_buttons:
    if button.text.strip() == "Posts": #replace with People and another filter mentioned top button
        button.click()
        break

# Open CSV file for writing
with open('linkedin_user_data.csv', mode='w', newline='', encoding='utf-8') as csv_file:
    csv_writer = csv.writer(csv_file)
    csv_writer.writerow(["Name", "Profile Link", "Description"])  # Write header row

    # Scroll and extract user details
    try:
        while True:
            users = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "update-components-actor"))
            )
            for user in users:
                try:
                    # Extract user details
                    name = user.find_element(By.CLASS_NAME, "update-components-actor__name").text
                    profile_link = user.find_element(By.CLASS_NAME, "update-components-actor__meta-link").get_attribute("href")
                    description = user.find_element(By.CLASS_NAME, "update-components-actor__description").text

                    # Write user data to CSV
                    csv_writer.writerow([name, profile_link, description])

                    # Check for policy violations
                    if check_policy_violation(description):
                        print(f"Flagged post by {name}: {description}")

                        # Ask for manual confirmation before reporting
                        user_input = input(f"Do you want to report this post (y/n)? Description: {description}\n")
                        if user_input.lower() == 'y':
                            # Report the post if confirmed by the user
                            report_button = user.find_element(By.CLASS_NAME, "update-components-actor__more-options")
                            report_button.click()

                            # Wait for the report menu to appear
                            time.sleep(random.uniform(2, 4))

                            # Click the 'Report' option
                            report_option = WebDriverWait(driver, 10).until(
                                EC.element_to_be_clickable((By.XPATH, "//span[text()='Report']"))
                            )
                            report_option.click()

                            # Optionally, select the reason (e.g., 'Spam', 'Inappropriate Content')
                            time.sleep(random.uniform(2, 4))  # Wait for modal to load

                            # Example of selecting a reason (e.g., 'Spam')
                            spam_option = WebDriverWait(driver, 10).until(
                                EC.element_to_be_clickable((By.XPATH, "//span[text()='Spam']"))
                            )
                            spam_option.click()

                            # Submit the report
                            submit_button = WebDriverWait(driver, 10).until(
                                EC.element_to_be_clickable((By.XPATH, "//button[text()='Submit']"))
                            )
                            submit_button.click()

                            print("Report submitted.")

                            # Add a delay after reporting to prevent overly aggressive reporting
                            time.sleep(random.uniform(10, 20))  # Throttle reporting frequency

                except Exception as e:
                    print(f"Error extracting user data: {e}")

            # Scroll down and wait for new content
            driver.execute_script("window.scrollBy(0, window.innerHeight);")
            time.sleep(random.uniform(5, 10))  # Randomized pause to simulate human behavior
    except KeyboardInterrupt:
        print("Scrolling stopped.")

# Close the browser
driver.quit()

def check_policy_violation(description):
    """
    Check if a post description violates LinkedIn's policies based on text content.
    """
    # Check for hate speech/harassment
    if any(keyword.lower() in description.lower() for keyword in HATE_SPEECH_KEYWORDS):
        return True

    # Check for spam content
    if any(keyword.lower() in description.lower() for keyword in SPAM_KEYWORDS):
        return True

    # Check for misinformation
    if any(keyword.lower() in description.lower() for keyword in MISINFORMATION_KEYWORDS):
        return True

    # Check for inappropriate content (e.g., nudity, violence)
    if any(keyword.lower() in description.lower() for keyword in INAPPROPRIATE_CONTENT_KEYWORDS):
        return True

    # No violations found
    return False


#NLP

# from transformers import pipeline
# import nltk
# from nltk.corpus import stopwords
#
# # Load a pre-trained sentiment analysis model
# sentiment_analyzer = pipeline("sentiment-analysis")
#
# # Download NLTK stopwords
# nltk.download('stopwords')
#
# def check_policy_violation(description):
#     """
#     Check if a post description violates LinkedIn's policies based on text content using NLP.
#     """
#     # Perform sentiment analysis on the post description
#     sentiment = sentiment_analyzer(description)
#
#     # If the sentiment is negative (e.g., toxic or harmful content)
#     if sentiment[0]['label'] == 'NEGATIVE' and sentiment[0]['score'] > 0.8:
#         return True
#
#     # Check for hate speech/harassment
#     if any(keyword.lower() in description.lower() for keyword in HATE_SPEECH_KEYWORDS):
#         return True
#
#     # Check for spam content
#     if any(keyword.lower() in description.lower() for keyword in SPAM_KEYWORDS):
#         return True
#
#     # Check for misinformation
#     if any(keyword.lower() in description.lower() for keyword in MISINFORMATION_KEYWORDS):
#         return True
#
#     # Check for inappropriate content (e.g., nudity, violence)
#     if any(keyword.lower() in description.lower() for keyword in INAPPROPRIATE_CONTENT_KEYWORDS):
#         return True
#
#     # No violations found
#     return False


