import json
import os
import re

import requests
from bs4 import BeautifulSoup


class ListingInfoGetter:
    def __init__(self, ref: str):
        url_base = "https://www.wg-gesucht.de"
        url = url_base + ref
        self.r = requests.get(url).text

    def get_listing_text(self):
        soup = BeautifulSoup(self.r, "lxml")
        ad_description = soup.find("div", {"id": "ad_description_text"}).find_all(
            ["p", "h3"]
        )
        text = []
        for chunk in ad_description:
            text.extend([chunk.getText().strip(), "\n\n"])
        text = "".join(text)
        return text

    @staticmethod
    def save_listing_text(file_name: str, text: str):
        if not os.path.exists(file_name):
            data = {"texts": [text]}
            with open(file_name, "w") as f:
                json.dump(data, f)

        with open(file_name, "r+") as f:
            data = json.load(f)
            data["texts"].append(text)
            f.seek(0)
            json.dump(data, f)

    def get_rental_length_months(self):
        soup = BeautifulSoup(self.r, "lxml")
        ps = soup.find_all("p", {"style": "line-height: 2em;"})
        dates = []
        for i, p in enumerate(ps):
            text = p.getText().strip()
            if "frei ab:" in text:
                text = text.replace("  ", "")
                dates = [elem for elem in re.split(" |\n", text) if "." in elem]
        if dates:
            return self._get_rental_length_months("-".join(dates))
        else:
            raise ValueError("Could not get rental dates!")

    @staticmethod
    def _get_rental_length_months(date_range_str: str) -> int:
        dates = date_range_str.split("-")
        if len(dates) != 2:
            # means listing is 'unbefristet'
            return -1
        start, end = date_range_str.split("-")
        start, end = start.strip(), end.strip()

        # year, month, day
        start_day, start_month, start_year = start.split(".")
        end_day, end_month, end_year = end.split(".")

        # get time difference in months
        date_diff = (int(end_year) - int(start_year)) * 12 + (
            int(end_month) - int(start_month)
        )
        return date_diff


if __name__ == "__main__":
    getter = ListingInfoGetter("/wg-zimmer-in-Berlin-Charlottenburg.9848754.html")
    # print(getter.get_listing_text())
    print(getter.get_rental_length_months())
