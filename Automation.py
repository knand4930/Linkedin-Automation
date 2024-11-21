import pyperclip
from dotenv import load_dotenv
import os
import time
import csv
import pickle
import random
from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
load_dotenv()

USER_NAME = os.environ.get("USER_NAME")
PASSWORD = os.environ.get("PASSWORD")
SEARCH_TERM = '''"you won"'''
FILTER_DATA=os.environ.get("FILTER_DATA")

HATE_SPEECH_KEYWORDS = ["racist", "bigotry", "hate speech", "xenophobia", "discrimination", "hateful"]
SPAM_KEYWORDS = ["free", "win", "won", "offer", "limited time", "claim your prize", "click here", "discount"]
MISINFORMATION_KEYWORDS = ["fake news", "misleading", "conspiracy theory", "false claim", "unverified"]
INAPPROPRIATE_CONTENT_KEYWORDS = ["nude", "sex", "pornography", "graphic", "violence", "abuse"]


def check_policy_violation(description):

    if any(keyword.lower() in description.lower() for keyword in HATE_SPEECH_KEYWORDS):
        return True

    if any(keyword.lower() in description.lower() for keyword in SPAM_KEYWORDS):
        return True

    if any(keyword.lower() in description.lower() for keyword in MISINFORMATION_KEYWORDS):
        return True

    if any(keyword.lower() in description.lower() for keyword in INAPPROPRIATE_CONTENT_KEYWORDS):
        return True

    return False

options = Options()
options.add_argument("--start-maximized")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

driver.get("https://www.linkedin.com/login")

try:
    with open('cookies.pkl', 'rb') as file:
        cookies = pickle.load(file)
        for cookie in cookies:
            driver.add_cookie(cookie)
    driver.refresh()
except FileNotFoundError:
    driver.find_element(By.ID, "username").send_keys(USER_NAME)
    driver.find_element(By.ID, "password").send_keys(PASSWORD)
    driver.find_element(By.ID, "password").send_keys(Keys.RETURN)
    with open('cookies.pkl', 'wb') as file:
        pickle.dump(driver.get_cookies(), file)

WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.CLASS_NAME, "search-global-typeahead__input"))
).send_keys(SEARCH_TERM, Keys.RETURN)

time.sleep(random.uniform(5, 10))

filter_buttons = WebDriverWait(driver, 10).until(
    EC.presence_of_all_elements_located((By.CLASS_NAME, "search-reusables__filter-pill-button"))
)
for button in filter_buttons:
    if button.text.strip() == FILTER_DATA:
        button.click()
        break

with open('linkedin_user_data.csv', mode='w', newline='', encoding='utf-8') as csv_file, \
     open('report_post.csv', mode='a', newline='', encoding='utf-8') as report_file:

    csv_writer = csv.writer(csv_file)
    csv_writer.writerow(["Name", "Profile Link", "Description"])

    report_writer = csv.writer(report_file)
    report_writer.writerow(['Name', 'Profile Link', 'Post Link', 'Description', 'Matched Keywords', 'Reason to Report', "Details"])


    try:
        while True:
            users = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "update-components-actor"))
            )
            for user in users:
                try:
                    name = user.find_element(By.CLASS_NAME, "update-components-actor__name").text
                    profile_link = user.find_element(By.CLASS_NAME, "update-components-actor__meta-link").get_attribute("href")
                    description = user.find_element(By.CLASS_NAME, "update-components-actor__description").text

                    csv_writer.writerow([name, profile_link, description])

                    if check_policy_violation(description):


                        matched_keywords = [kw for kw in
                                            HATE_SPEECH_KEYWORDS + SPAM_KEYWORDS + MISINFORMATION_KEYWORDS + INAPPROPRIATE_CONTENT_KEYWORDS
                                            if kw.lower() in description.lower()]

                        reason_to_report = None
                        if any(kw in description.lower() for kw in SPAM_KEYWORDS):
                            reason_to_report = "Spam"
                        elif any(kw in description.lower() for kw in HATE_SPEECH_KEYWORDS):
                            reason_to_report = "Hateful speech"
                        elif any(kw in description.lower() for kw in MISINFORMATION_KEYWORDS):
                            reason_to_report = "Misinformation"
                        elif any(kw in description.lower() for kw in INAPPROPRIATE_CONTENT_KEYWORDS):
                            reason_to_report = "Sexual content"



                        time.sleep(10)
                        unique_name_parts = list(dict.fromkeys(name.split()))
                        cleaned_name = " ".join(unique_name_parts)

                        flagged_user = cleaned_name

                        try:
                            control_button = driver.find_element(By.XPATH,
                                                                 f"//button[contains(@aria-label, 'Open control menu for post by {cleaned_name}')]")
                            control_button.click()
                            time.sleep(5)

                            dropdown_content = WebDriverWait(driver, 10).until(
                                EC.presence_of_element_located((By.CLASS_NAME, "artdeco-dropdown__content-inner"))
                            )

                            # Get the HTML source of the dropdown content
                            # dropdown_html = dropdown_content.get_attribute("outerHTML")
                            # print("Dropdown Content HTML:")
                            # print(dropdown_html)


                            time.sleep(5)
                            copy_link_option = WebDriverWait(driver, 10).until(
                                EC.presence_of_element_located(
                                    (By.XPATH, "//h5[text()='Copy link to post']/ancestor::div[@role='button']"))
                            )
                            copy_link_option.click()

                            WebDriverWait(driver, 2)

                            copied_url = pyperclip.paste()

                            time.sleep(5)

                            report_control_button = driver.find_element(By.XPATH,
                                                                 f"//button[contains(@aria-label, 'Open control menu for post by {cleaned_name}')]")
                            report_control_button.click()

                            time.sleep(5)

                            report_dropdown_content = WebDriverWait(driver, 10).until(
                                EC.presence_of_element_located((By.CLASS_NAME, "artdeco-dropdown__content-inner"))
                            )

                            report_post_option = WebDriverWait(driver, 10).until(
                                EC.presence_of_element_located(
                                    (By.XPATH, "//h5[text()='Report post']/ancestor::div[@role='button']"))
                            )
                            report_post_option.click()

                            print(reason_to_report, "reason_to_report")

                            time.sleep(2)
                            if reason_to_report:
                                try:
                                    reason_button = WebDriverWait(driver, 10).until(
                                        EC.element_to_be_clickable(
                                            (By.XPATH, f"//button[@aria-label='{reason_to_report}']"))
                                    )

                                    reason_button.click()
                                    print("Report button clicked !!")
                                except Exception as e:
                                    print(f"Error Report button clicked: {e}")

                                time.sleep(5)
                                try:

                                    next_button = WebDriverWait(driver, 10).until(
                                        EC.element_to_be_clickable((By.XPATH, "//button[.//span[text()='Next']]"))
                                    )
                                    next_button.click()

                                    print("next button clicked !!")
                                except Exception as e:
                                    print(f"Error next button clicked: {e}")

                                try:

                                    checkbox = WebDriverWait(driver, 10).until(
                                                    EC.element_to_be_clickable((By.ID, "urn:li:fsd_formElement:urn:li:fsd_contentReportingFormElement:notificationsOptIn-0"))
                                                )

                                    checkbox.click()
                                    print("Checkbox clicked.")
                                except Exception as e:
                                    print(f"Error clicking the checkbox: {e}")

                                try:
                                    submit_button = WebDriverWait(driver, 10).until(
                                        EC.element_to_be_clickable((By.XPATH,
                                                                    "//button[@data-test-trust-button-action-component-button='SUBMIT']"))
                                    )

                                    submit_button.click()
                                    print("Submit report button clicked.")
                                except Exception as e:
                                    print(f"Error clicking the submit report button: {e}")

                                print(f"Report submitted for {name} with reason: {reason_to_report}")

                                report_data_values = f"Report submitted for {name} with reason: {reason_to_report}"

                                report_writer.writerow(
                                    [flagged_user, profile_link, copied_url, description, ', '.join(matched_keywords),
                                     reason_to_report, report_data_values]
                                )

                            time.sleep(300)

                        except Exception as e:
                            print(f"Error during reporting: {e}")


                except Exception as e:
                    print(f"Error extracting user data: {e}")

            driver.execute_script("window.scrollBy(0, window.innerHeight);")
            time.sleep(random.uniform(5, 10))
    except KeyboardInterrupt:
        print("Scrolling stopped.")

driver.quit()
