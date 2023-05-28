# -*- coding: utf-8 -*-
import json
import time

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains

WAIT_TIME = 20


def get_login_credentials():
    with open("login-creds.json", "r") as f:
        return json.load(f)


def submit_app(ref):
    # change the location of the driver on your machine
    # create ChromeOptions object
    chrome_options = webdriver.ChromeOptions()
    creds = get_login_credentials()

    # add the argument to reuse an existing tab
    chrome_options.add_argument("--reuse-tab")

    # create the ChromeDriver object
    driver = webdriver.Chrome("/usr/local/bin/chromedriver", options=chrome_options)
    driver.get("https://www.wg-gesucht.de/nachricht-senden/" + ref)
    driver.implicitly_wait(WAIT_TIME)
    accept_button = driver.find_elements(
        "xpath", "//*[contains(text(), 'Accept all')]"
    )[0]
    accept_button.click()
    konto_button = driver.find_elements("xpath", "//*[contains(text(), 'Mein Konto')]")[
        0
    ]
    konto_button.click()
    driver.implicitly_wait(WAIT_TIME)
    email = driver.find_element("id", "login_email_username")
    email.send_keys(creds["email"])
    driver.implicitly_wait(WAIT_TIME)
    passwd = driver.find_element("id", "login_password")
    passwd.send_keys(creds["password"])
    driver.implicitly_wait(WAIT_TIME)
    login_button1 = driver.find_element("id", "login_submit")
    driver.implicitly_wait(WAIT_TIME)
    login_button1.click()
    driver.implicitly_wait(WAIT_TIME)
    try:
        se_button1 = driver.find_element("id", "sicherheit_bestaetigung")
        se_button1.click()
    except:
        print("No sicherheit check")

    # checks if already sent message to flat posting.
    try:
        timestamp = driver.find_element("id", "message_timestamp")
        print("Timestamp = ", timestamp)
        print("Message has been sent. Will skip")
        driver.quit()
    except:
        print("No message has been sent. Will send now...")

    text_area = driver.find_element("id", "message_input")
    text_area.clear()

    # read your message from a file
    try:
        message_file = open("./message.txt", "r")
        message = message_file.read()
        print(message)
        text_area.send_keys(message)
        message_file.close()
    except:
        print("message.txt file not found!")
        return 0

    # driver.implicitly_wait(10)
    time.sleep(WAIT_TIME)  # may not be required
    try:
        submit_button = driver.find_element(
            "xpath",
            "//button[@data-ng-click='submit()' or contains(.,'Nachricht senden')]",
        )
        submit_button.click()
    except NoSuchElementException:
        print("Cannot find submit button!")
        driver.quit()
    driver.quit()
