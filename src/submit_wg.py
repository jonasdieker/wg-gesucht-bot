# -*- coding: utf-8 -*-
import json
import os
import random
import time

from selenium import webdriver
from selenium.common.exceptions import (
    ElementNotInteractableException,
    NoSuchElementException,
    StaleElementReferenceException,
    TimeoutException,
)
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from src import OpenAIHelper


def valid_json(json_str: str) -> bool:
    try:
        json.loads(json_str)
    except ValueError as e:
        return False
    return True


def get_element(driver, by, id):
    ignored_exceptions = (
        StaleElementReferenceException,
        NoSuchElementException,
        ElementNotInteractableException,
    )
    try:
        wait = WebDriverWait(driver, 10, poll_frequency=1)
        element = wait.until(EC.visibility_of_element_located((by, id)))
    except TimeoutException:
        wait = WebDriverWait(driver, 30, poll_frequency=1)
        element = wait.until(EC.presence_of_element_located((by, id)))
    if isinstance(element, list):
        element = element[0]
    return element


def click_button(driver, by, id):
    try:
        element = get_element(driver, by, id)
        driver.implicitly_wait(2)
        element.click()
    except ElementNotInteractableException:
        raise ElementNotInteractableException()


def send_keys(driver, by, id, send_str):
    try:
        element = get_element(driver, by, id)
        element.send_keys(send_str)
    except ElementNotInteractableException:
        raise ElementNotInteractableException(f"Could not enter: {send_str}")


def gpt_get_language(config) -> str:
    openai = OpenAIHelper(config["openai_credentials"]["api_key"])
    listing_text = config['listing_text']
    prompt = f"""What language is this:
    '{listing_text}'
    Please only respond in a JSON style format like 'language: '<your-answer>',
    where your answer should be a single word which is the language."""
    response = openai.generate(prompt)
    if valid_json(response):
        return response["language"]
    return ""


def gpt_get_keyword(openai_helper, config) -> str:
    pass


def submit_app(config, logger):
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--log-level=3")

    # add the argument to reuse an existing tab
    if config["run_headless"]:
        chrome_options.headless = True
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--reuse-tab")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")

    # create the ChromeDriver object and log
    try:
        service_log_path = "chromedriver.log"
        service_args = ["--verbose"]
        driver = webdriver.Chrome(
            "/usr/bin/chromedriver",
            options=chrome_options,
            service_args=service_args,
            service_log_path=service_log_path,
        )
        # mainly when using screen
        driver.maximize_window()
        driver.get("https://www.wg-gesucht.de/nachricht-senden" + config["ref"])
    except:
        logger.log(
            "Chrome crashed! You might be trying to run it without a screen in terminal?"
        )
        driver.quit()
        return False

    driver.implicitly_wait(2)

    # accept cookies button
    click_button(driver, By.XPATH, "//*[contains(text(), 'Accept all')]")

    # my account button
    click_button(driver, By.XPATH, "//*[contains(text(), 'Mein Konto')]")

    driver.implicitly_wait(2)

    # enter email
    send_keys(
        driver, By.ID, "login_email_username", config["wg_gesucht_credentials"]["email"]
    )

    # enter password
    send_keys(
        driver, By.ID, "login_password", config["wg_gesucht_credentials"]["password"]
    )

    # login button
    click_button(driver, By.ID, "login_submit")
    logger.info("Logged in.")

    driver.implicitly_wait(2)

    # occasionally wg-gesucht gives you advice on how to stay safe.
    try:
        click_button(driver, By.ID, "sicherheit_bestaetigung")
    except:
        logger.info("No security check.")

    # driver.implicitly_wait(5)
    time.sleep(2)

    # checks if its possible to sent message to listing.
    try:
        # _ = get_element(driver, By.ID, "message_timestamp")
        _ = get_element(driver, By.XPATH, '//*[@id="last_message_id_895679322"]/div')
        logger.info("Message has already been sent previously. Will skip this offer.")
        driver.quit()
        return False
    except:
        logger.info("No message has been sent. Will send now...")

    driver.implicitly_wait(2)

    logger.info(f"Sending to: {config['user_name']}, {config['address']}.")

    text_area = get_element(driver, By.ID, "message_input")
    if text_area:
        text_area.clear()

    languages = list(config["messages"].keys())
    if len(languages) == 1:
        message_file = config["messages"][languages[0]]
        logger.info(f"Selected text in {languages[0]}")
    else:
        if config["openai_credentials"]["api_key"] == "":
            # no openai key so just use first language in list
            message_file = config["messages"][languages[0]]
            logger.info(f"No openai api key -> selected text in {languages[0]}")
        else:
            # check which languages user want to message in using GPT
            listing_language = gpt_get_language(config).lower()
            logger.info(f"Listing language is: {listing_language}.")
            if listing_language in languages:
                message_file = config["languages"][listing_language]
                logger.info(f"Selected text in {listing_language}.")
            else:
                logger.info(
                    f"Listing language does not overlap with available texts in {languages}. Using first languages in list."
                )
                message_file = config["messages"][languages[0]]

    logger.info("auto quit ...")
    driver.quit()
    time.sleep(2)
    return False
    # read message from a file
    try:
        message_file = open(f"./{message_file}", "r")
        message = str(message_file.read())
        message = message.replace("receipient", config["user_name"].split(" ")[0])
        print(message)
        time.sleep(20000)
        text_area.send_keys(message)
        message_file.close()
    except:
        logger.info(f"{message_file} file not found!")
        driver.quit()
        return False

    # TODO: further message processing!
    # f"""This is my info:
    # {}
    # This is the question: {}.
    # Please respond to question based on my info."""

    driver.implicitly_wait(2)

    try:
        click_button(
            driver,
            By.XPATH,
            "//button[@data-ng-click='submit()' or contains(.,'Nachricht senden')]",
        )
        logger.info(f">>>> Message sent to: {config['ref']} <<<<")
        driver.implicitly_wait(2)
        driver.quit()
        return True
    except ElementNotInteractableException:
        logger.info("Cannot find submit button!")
        driver.quit()
        return False
