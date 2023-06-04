import scrapy


class QuotesSpider(scrapy.Spider):
    name = "wg-gesucht"
    start_urls = [
        "https://www.wg-gesucht.de/wg-zimmer-in-Berlin.8.0.1.0.html?csrf_token=c9280a89ddcd56ac55c721ab68f7c5fd64996ca7&offer_filter=1&city_id=8&sort_column=0&sort_order=0&noDeact=1&categories%5B%5D=0&rent_types%5B%5D=2&rent_types%5B%5D=1&rent_types%5B%5D=2%2C1&sMin=18&ot%5B%5D=126&ot%5B%5D=132&ot%5B%5D=85079&ot%5B%5D=151&ot%5B%5D=163&ot%5B%5D=85086&ot%5B%5D=165&wgSea=2&wgMnF=2&wgArt%5B%5D=6&wgArt%5B%5D=12&wgArt%5B%5D=11&wgArt%5B%5D=19&wgArt%5B%5D=22&wgSmo=2&exc=2&img_only=1"
    ]

    def parse(self, response):
        for quote in response.css("h3.truncate_title a::attr(href)").extract():
            if (
                "airbnb.pvxt.net" in quote
                or "housinganywhere.com" in quote
                or "roomlessrent" in quote
                or "asset_id" in quote
            ):
                pass
            else:
                yield {"data-id": quote}
