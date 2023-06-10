from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
import re
import pprint


class ListingGetter:
    def __init__(self, url):
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url)
            html = page.inner_html("#main_column")   
        
        soup = BeautifulSoup(html, "lxml")
        self.soup = soup

    def get_all_infos(self):
        info_dict = {}
        refs = self.get_refs()
        user_names = self.get_users()
        addresses, wg_types = self.get_address_wg()
        rental_lengths_months = self.get_rental_length_months()
        for i, (ref, user_name, address, wg_type, rental_length_months) in enumerate(zip(refs, user_names, addresses, wg_types, rental_lengths_months)):
            listing_dict = {}
            listing_dict["ref"], listing_dict["user_name"] = ref, user_name
            listing_dict["address"], listing_dict["wg_type"] = address, wg_type
            listing_dict["rental_length_months"] = rental_length_months
            info_dict[i] = listing_dict
        return info_dict

    def get_refs(self):
        elements = self.soup.find_all("a", href=True)
        listings = set()
        for el in elements:
            href = el["href"]
            if ".html" == href[-5:] and "/" == href[0]:
                listings.add(href)
        return listings

    def get_users(self):
        users = list()
        elements = self.soup.find_all("span", {"class": "ml5"})
        for element in elements:
            text = element.getText()
            users.append(text)
        return users

    def get_address_wg(self):
        address = list()
        wg_type = list()
        elements = self.soup.find_all("div", {"class": "col-xs-11"})
        for el in elements:
            text = el.find("span").getText()
            parts = [part.strip() for part in re.split("\||\n", text) if part.strip() != ""]
            wg_type.append(parts[0])
            address.append(", ".join(parts[::-1][:-1]))
        return address, wg_type

    def get_rental_length_months(self):
        rental_length_months = []
        elements = self.soup.find_all("div", {"class": "col-xs-5 text-center"})
        for el in elements:
            text = el.getText()
            start_end = [part.strip() for part in re.split("-|\n", text) if part.strip() != ""]
            rental_length_months.append(self._get_rental_length_months("-".join(start_end)))
        return rental_length_months

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
    url = "https://www.wg-gesucht.de/wg-zimmer-in-Berlin.8.0.1.0.html?csrf_token=c9280a89ddcd56ac55c721ab68f7c5fd64996ca7&offer_filter=1&city_id=8&sort_column=0&sort_order=0&noDeact=1&categories%5B%5D=0&rent_types%5B%5D=2&rent_types%5B%5D=1&rent_types%5B%5D=2%2C1&sMin=14&ot%5B%5D=126&ot%5B%5D=132&ot%5B%5D=85079&ot%5B%5D=151&ot%5B%5D=163&ot%5B%5D=85086&ot%5B%5D=165&wgSea=2&wgMnF=2&wgArt%5B%5D=6&wgArt%5B%5D=12&wgArt%5B%5D=11&wgArt%5B%5D=19&wgArt%5B%5D=22&wgSmo=2&exc=2&img_only=1"
    listings_getter = ListingGetter(url)
    info_dict = listings_getter.get_all_infos()
    pprint.pprint(info_dict)
