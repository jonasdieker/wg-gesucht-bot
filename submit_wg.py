# -*- coding: utf-8 -*-
import json
import random
import time

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException, ElementNotInteractableException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

def get_login_credentials():
    with open("login-creds.json", "r") as f:
        return json.load(f)


def get_random_wait_time():
    return random.uniform(5, 10)


def get_element(driver, by, id):
    try:
        element = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((by, id))
        )
    except NoSuchElementException:
        driver.quit()
        raise NoSuchElementException()
    except TimeoutException:
        element = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((by, id)))
    if isinstance(element, list):
        element = element[0]
    return element


def click_button(driver, by, id):
    try:
        element = get_element(driver, by, id)
        element.click()
    except ElementNotInteractableException:
        raise ElementNotInteractableException()
        

def send_keys(driver, by, id, send_str):
    try:
        element = get_element(driver, by, id)
        element.send_keys(send_str)
    except ElementNotInteractableException:
        raise ElementNotInteractableException(f"Could not enter: {send_str}")


def submit_app(ref, logger, args, messages_sent):

    chrome_options = webdriver.ChromeOptions()
    creds = get_login_credentials()

    # add the argument to reuse an existing tab
    if args.launch_type == "headless":
        chrome_options.headless = True
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--reuse-tab")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    elif args.launch_type == "non-headless":
        pass
    else:
        raise NotImplementedError(
            "Entered unsupported 'launch_type'. Please choose from {'headless', non-headless}"
        )
    # chrome_options.add_argument("--no-sandbox")
    # chrome_options.add_argument("--disable-dev-shm-usage")
    # chrome_options.add_argument("--headless")

    # create the ChromeDriver object
    try:
        service_log_path = "chromedriver.log"
        service_args = ["--verbose"]
        driver = webdriver.Chrome("/usr/bin/chromedriver", options=chrome_options, service_args=service_args, service_log_path=service_log_path)
        driver.get("https://www.wg-gesucht.de/nachricht-senden/" + ref)
    except:
        logger.log("Chrome crashed! You might be trying to run it without a screen in terminal? Look at 'chromedriver.log'.")
        driver.quit()

    # mainly when using screen
    driver.maximize_window()

    # accept cookies button
    click_button(driver, By.XPATH, "//*[contains(text(), 'Accept all')]")

    # my account button
    click_button(driver, By.XPATH, "//*[contains(text(), 'Mein Konto')]")

    time.sleep(2)

    # enter email
    send_keys(driver, By.ID, "login_email_username", creds["email"])

    # enter password
    send_keys(driver, By.ID, "login_password", creds["password"])

    # login button
    click_button(driver, By.ID, "login_submit")

    # occasionally wg-gesucht gives you advice on how to stay safe.
    try:
        se_button1 = get_element(driver, By.ID, "sicherheit_bestaetigung")
        se_button1.click()
    except:
        logger.info("No security check.")

    # checks if its possible to sent message to listing.
    try:
        _ = get_element(driver, By.ID, "message_timestamp")
        logger.info("Message has already been sent previously. Will skip this offer.")
        driver.quit()
        return None
    except:
        logger.info("No message has been sent. Will send now...")

    # Get user name and listing address to compare to previous ones
    listing_user = get_element(driver, By.XPATH, '//*[@id="start_new_conversation"]/div[3]/div[1]/label/b').text
    listing_user = " ".join(listing_user.split(" ")[2:])
    listing_address = get_element(driver, By.XPATH, '//*[@id="ad_details_card"]/div[1]/div[2]/div[1]/div[2]').text
    info_to_store = listing_user + " " + listing_address
    if info_to_store in messages_sent:
        # this means that the user reuploaded the listing -> should skip
        logger.info("Listing was reuploaded and has been contacted in the past! Skipping ...")
        driver.quit()
        return None

    text_area = get_element(driver, By.ID, "message_input")
    if text_area:
        text_area.clear()

    # read your message from a file
    try:
        message_file = open("./message.txt", "r")
        message = message_file.read()
        time.sleep(get_random_wait_time())
        text_area.send_keys(message)
        message_file.close()
    except:
        logger.info("message.txt file not found!")
        return None

    time.sleep(2)

    try:
        click_button(driver,
            By.XPATH,
            "//button[@data-ng-click='submit()' or contains(.,'Nachricht senden')]",
            )
        logger.info(f">>>> Message sent to: {ref} <<<<")
        time.sleep(3)
        driver.quit()
        return info_to_store
    except ElementNotInteractableException:
        logger.info("Cannot find submit button!")
        driver.quit()
        return None
