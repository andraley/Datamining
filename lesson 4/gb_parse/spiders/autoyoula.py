import scrapy
from ..loaders import AutoyoulaLoader


pages = {
    "brands": "//div[@data-target='transport-main-filters']/"
    "div[contains(@class, 'TransportMainFilters_brandsList')]//"
    "a[@data-target='brand']/@href",
}

brands = {
    "pagination": '//a[@data-target-id="button-link-serp-paginator"]/@href',
    "car": '//article[@data-target="serp-snippet"]//a[@data-target="serp-snippet-title"]/@href',
}

cars = {
    "title": {"xpath": "//div[@data-target='advert-title']/text()"},
    "photos": {"xpath": "//figure/picture/img/@src"},
    "characteristics": {
        "xpath": "//h3[contains(text(), 'Характеристики')]/..//"
        "div[contains(@class, 'AdvertSpecs_row')]"
    },
    "price": {"xpath": '//div[@data-target="advert"]//div[@data-target="advert-price"]/text()'},
    "descriptions": {
        "xpath": '//div[@data-target="advert"]//'
        'div[@data-target="advert-info-descriptionFull"]/text()'
    },
    "author": {
        "xpath": '//script[contains(text(), "window.transitState = decodeURIComponent")]',
        "re": r"youlaId%22%2C%22([a-zA-Z|\d]+)%22%2C%22avatar",
    },
}


class AutoyoulaSpider(scrapy.Spider):
    name = "autoyoula"
    allowed_domains = ["auto.youla.ru"]
    start_urls = ["https://auto.youla.ru/"]

    def _get_follow_xpath(self, response, select_str, callback, **kwargs):
        for link in response.xpath(select_str):
            yield response.follow(link, callback=callback, cb_kwargs=kwargs)

    def parse(self, response, *args, **kwargs):
        yield from self._get_follow_xpath(
            response, pages["brands"], self.brand_parse
        )

    def brand_parse(self, response, **kwargs):
        callbacks = {
            "pagination": self.brand_parse,
            "car": self.car_parse,
        }
        for key, value in brands.items():
            yield from self._get_follow_xpath(
                response, value, callbacks[key],
            )

    def car_parse(self, response):
        loader = AutoyoulaLoader(response=response)
        loader.add_value("url", response.url)
        for key, xpath in cars.items():
            loader.add_xpath(key, **xpath)
        yield loader.load_item()

