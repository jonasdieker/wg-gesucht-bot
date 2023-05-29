# -*- coding: utf-8 -*-
import json
import random
import time

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
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
            EC.presence_of_all_elements_located((by, id))
        )
    except NoSuchElementException or TimeoutException:
        driver.quit()
        return None
    if isinstance(element, list):
        element = element[0]
    return element


def submit_app(ref, logger):
    # change the location of the driver on your machine
    # create ChromeOptions object
    chrome_options = webdriver.ChromeOptions()
    creds = get_login_credentials()

    # add the argument to reuse an existing tab
    chrome_options.headless = True
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--reuse-tab")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    # chrome_options.add_argument("--no-sandbox")
    # chrome_options.add_argument("--disable-dev-shm-usage")
    # chrome_options.add_argument("--headless")

    # create the ChromeDriver object
    driver = webdriver.Chrome("/usr/local/bin/chromedriver", options=chrome_options)
    driver.get("https://www.wg-gesucht.de/nachricht-senden/" + ref)
    driver.maximize_window()

    accept_button = get_element(driver, By.XPATH, "//*[contains(text(), 'Accept all')]")
    if accept_button:
        accept_button.click()

    konto_button = get_element(driver, By.XPATH, "//*[contains(text(), 'Mein Konto')]")
    if konto_button:
        konto_button.click()

    time.sleep(2)

    email = get_element(driver, By.ID, "login_email_username")
    if email:
        email.send_keys(creds["email"])

    passwd = get_element(driver, By.ID, "login_password")
    if passwd:
        passwd.send_keys(creds["password"])

    login_button1 = get_element(driver, By.ID, "login_submit")
    if login_button1:
        login_button1.click()

    try:
        se_button1 = get_element(driver, By.ID, "sicherheit_bestaetigung")
        se_button1.click()
    except:
        logger.info("No security check.")

    # checks if already sent message to flat posting.
    try:
        # driver.find_element("id", "message_timestamp")
        _ = get_element(driver, By.ID, "message_timestamp")
        logger.info("Message has already been sent previously. Will skip this offer.")
        driver.quit()
        return
    except:
        logger.info("No message has been sent. Will send now...")

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
        return 0

    try:
        submit_button = get_element(
            driver,
            By.XPATH,
            "//button[@data-ng-click='submit()' or contains(.,'Nachricht senden')]",
        )
        submit_button.click()
        logger.info(f">>>> Message sent to: {ref} <<<<")
    except NoSuchElementException:
        logger.info("Cannot find submit button!")
        driver.quit()
    driver.quit()
