from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright



def get_listings(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url)
        html = page.inner_html("#main_column")

    soup = BeautifulSoup(html, "lxml")
    elements = soup.find_all("a", href=True)
    listings = set()
    for el in elements:
        href = el["href"]
        if ".html" == href[-5:] and "/" == href[0]:
            listings.add(href)
    return listings


if __name__ == "__main__":
    url = "https://www.wg-gesucht.de/wg-zimmer-in-Berlin.8.0.1.0.html?csrf_token=c9280a89ddcd56ac55c721ab68f7c5fd64996ca7&offer_filter=1&city_id=8&sort_column=0&sort_order=0&noDeact=1&categories%5B%5D=0&rent_types%5B%5D=2&rent_types%5B%5D=1&rent_types%5B%5D=2%2C1&sMin=14&ot%5B%5D=126&ot%5B%5D=132&ot%5B%5D=85079&ot%5B%5D=151&ot%5B%5D=163&ot%5B%5D=85086&ot%5B%5D=165&wgSea=2&wgMnF=2&wgArt%5B%5D=6&wgArt%5B%5D=12&wgArt%5B%5D=11&wgArt%5B%5D=19&wgArt%5B%5D=22&wgSmo=2&exc=2&img_only=1"
    listings = get_listings(url)
    print(len(listings))
    for el in listings:
        print(el)