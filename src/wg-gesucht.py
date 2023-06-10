import json
import logging
import os.path
import time
from subprocess import call

import yaml

import submit_wg
from get_listing_text import ListingInfoGetter

logging.basicConfig(
    format="[%(asctime)s | %(levelname)s] - %(message)s ",
    level=logging.INFO,
    datefmt="%Y-%m-%d_%H:%M:%S",
    handlers=[logging.FileHandler("../debug.log"), logging.StreamHandler()],
)
logger = logging.getLogger("bot")


def scrape_site():
    call(
        [
            "scrapy",
            "crawl",
            "wg-gesucht",
            "-o",
            "wg_offer.json",
            "-s",
            "LOG_ENABLED=false",
        ]
    )
    with open("wg_offer.json", "r") as data_file:
        data = json.load(data_file)
    data = list(set([i["data-id"] for i in data]))
    if os.path.isfile("wg_offer_old.json"):
        with open("wg_offer_old.json", "r") as data_old_file:
            if len(data_old_file.readlines()) != 0:
                data_old_file.seek(0)
                data_old = json.load(data_old_file)
            else:
                data_old = []
        data_old = list(set([i["data-id"] for i in data_old]))
    else:
        data_old = []
    return data, data_old


def clear_json_files():
    files = ["wg_offer.json", "wg_offer_old.json"]
    for file in files:
        with open(file, "w") as f:
            json.dump({}, f)


def main(args):
    clear_json_files()
    fname = "wg_offer.json"
    while True:
        if os.path.isfile(fname):
            logger.info("Scrape wg-gesucht.de for new offers.")
            call(["mv", fname, "wg_offer_old.json"])
            data, data_old = scrape_site()
        else:
            logger.info("No 'wg_offer.json' file found.")
            data, data_old = scrape_site()

        if not os.path.isfile("messages_sent.txt"):
            with open("messages_sent.txt", "w") as f:
                pass

        diff_id = list(set(data) - set(data_old))
        with open("messages_sent.txt", "r") as msgs:
            messages_sent = msgs.readlines()
        if len(diff_id) != 0:
            logger.info(f"Found {len(diff_id)} new offers.")
            for ref in diff_id:
                # avoid messaging letting agencies
                if len(ref.split("/")) > 2:
                    continue
                logger.info(f"Trying to send message to: {ref}")

                # get listing info which can be retrieved from html and store in args
                listing_info_getter = ListingInfoGetter(ref)
                listing_text = listing_info_getter.get_listing_text()
                listing_length_months = listing_info_getter.get_rental_length_months()
                args["listing_text"] = listing_text
                args["listing_length_months"] = listing_length_months

                # use selenium to retrieve dynamically loaded info and send message
                info_to_store = submit_wg.submit_app(ref, logger, args, messages_sent)

                # if new message sent -> store information about listing
                if info_to_store:
                    with open("messages_sent.txt", "a") as msgs:
                        msgs.write(f"{info_to_store}\n")
                    listing_info_getter.save_listing_text(
                        "listing_texts.json", listing_text
                    )

        else:
            logger.info("No new offers.")
        logger.info("Sleep.")
        time.sleep(5)


if __name__ == "__main__":
    with open("config.yaml", "r") as stream:
        config = yaml.safe_load(stream)
    main(config)
