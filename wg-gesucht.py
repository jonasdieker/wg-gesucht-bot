import json
import logging
import os.path
import time
from subprocess import call

import yaml

from src import (
    submit_wg,
    ListingGetter,
    ListingInfoGetter,

)

logging.basicConfig(
    format="[%(asctime)s | %(levelname)s] - %(message)s ",
    level=logging.INFO,
    datefmt="%Y-%m-%d_%H:%M:%S",
    handlers=[logging.FileHandler("../debug.log"), logging.StreamHandler()],
)
logger = logging.getLogger("bot")


def main(config):
    """
    Operations:
     - Get newest listings
     - Compares them with previous listing (if available)
     - For all new listings not present in previous listings:
        - Checks rental length of listing
        - Checks if listing is reupload by comparing to user_name and address
        - Gets listing text -> can be used for OpenAI further down the line
        - Attemps to submit an application
        - Adds listing to 'past_listings.txt'
    """

    # initialise old listings for later
    old_listings = dict()

    while True:
        # read previously sent messages:
        past_listings_file_name = "past_listings.txt"
        if not os.path.exists(past_listings_file_name):
            prev_listings = []
        else:
            with open(past_listings_file_name, "r") as msgs:
                prev_listings = msgs.readlines()
        
        # get current listings
        url = config["url"]
        listing_getter = ListingGetter(url)
        info_dict = listing_getter.get_all_infos()
        new_listings = info_dict

        # get diff: new - old listings
        old_values = old_listings.values()
        diff_dict = {k: v for k, v in enumerate(new_listings.values()) if v not in old_values}
        if diff_dict:
            logger.info(f"Found {len(diff_dict)} new listings.")
            for listing in diff_dict.values():
                # unpack listing dict
                ref = listing["ref"]
                listing_length_months = listing["rental_length_months"]

                # add to config for submit_app function
                config["ref"] = ref
                config["user_name"] = listing["user_name"]
                config["address"] = listing["address"]
                logger.info(f"Trying to send message to: {listing}")

                # check rental length, if below min -> skip this listing
                min_rental_length_months = config["min_listing_length_months"]
                if listing_length_months >= 0 and listing_length_months < min_rental_length_months:
                    logger.info(
                                f"Rental period of {listing_length_months} months is below required {min_rental_length_months} months. Skipping ..."
                                )
                    continue

                # check if already messaged listing in the past
                listings_sent_identifier = f"{listing['user_name']}: {listing['address']}\n"
                if listings_sent_identifier in prev_listings:
                    logger.info("Listing in 'prev_listings' file, therfore contacted in the past! Skipping ...")
                    continue

                # get listing text and store in config for later processing
                listing_info_getter = ListingInfoGetter(ref)
                listing_text = listing_info_getter.get_listing_text()
                config["listing_text"] = listing_text

                # use selenium to retrieve dynamically loaded info and send message
                sending_successful = submit_wg.submit_app(config, logger)

                # if new message sent -> store information about listing
                if sending_successful:
                    listing_info_getter.save_listing_text(
                        "listing_texts.json", listing_text
                    )
                
                # add listing to past_listings.txt
                with open(past_listings_file_name, "a") as msgs:
                    msgs.write(f"{listings_sent_identifier}")
            old_listings = new_listings.copy()
        else:
            logger.info("No new offers.")
        logger.info("Sleep.")
        time.sleep(60)


if __name__ == "__main__":
    with open("config.yaml", "r") as stream:
        config = yaml.safe_load(stream)
    main(config)
