import json
import os.path
import time
from datetime import datetime
from subprocess import call

import submit_wg

fname = "wg_offer.json"


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
            json.dumps({})


def main():
    clear_json_files()
    while True:
        if os.path.isfile(fname):
            print("'wg_offer.json' file found.")
            call(["mv", fname, "wg_offer_old.json"])
            data, data_old = scrape_site()
        else:
            print("No 'wg_offer.json' file found.")
            data, data_old = scrape_site()

        if os.path.isfile("wg_blacklist.json"):
            with open("wg_blacklist.json") as blacklist:
                blacklist = json.load(blacklist)
            blacklist = list(set([i["data-id"] for i in blacklist]))
        else:
            blacklist = []
        print("Blacklist: ", blacklist)

        diff_id = list(set(data) - set(data_old) - set(blacklist))

        text_file = open("wg_sent_request.dat", "a")
        text_file1 = open("wg_diff.dat", "a")
        if len(diff_id) != 0:
            print(len(diff_id), "new offers found")
            print("New offers id:", diff_id)
            print("Time: ", datetime.now())
            for new in diff_id:
                # avoid adding adds to list
                if len(new.split("/")) > 2:
                    continue
                print("Sending message to: ", new)
                submit_wg.submit_app(new)
                text_file.write("ID: %s \n" % new)
                text_file.write(str(datetime.now()) + "\n")
                text_file1.write(str(new) + "\n")
            text_file.close()
            text_file1.close()
        else:
            print("No new offers.")
            print("Time: ", datetime.now())
        time.sleep(5)


if __name__ == "__main__":
    main()
