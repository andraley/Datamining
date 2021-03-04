import scrapy
import pymongo
import re


class AutoyoulaSpider(scrapy.Spider):
    name = 'autoyoula'
    allowed_domains = ['auto.youla.ru']
    start_urls = ['http://auto.youla.ru/']
    _css_selectors = {
        "brands": "div.TransportMainFilters_brandsList__2tIkv "
        ".ColumnItemList_item__32nYI a.blackLink",
        "pagination": "div.Paginator_block__2XAPy a.Paginator_button__u1e7D",
        "car": "article.SerpSnippet_snippet__3O1t2 .SerpSnippet_titleWrapper__38bZM a.blackLink",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.db_client = pymongo.MongoClient()

    def _get_follow(self, response, select_str, callback, **kwargs):
        for a in response.css(select_str):
            link = a.attrib.get("href")
            yield response.follow(link, callback=callback, cb_kwargs=kwargs)

    def parse(self, response, *args, **kwargs):
        yield from self._get_follow(response, self._css_selectors["brands"], self.brand_parse)

    def brand_parse(self, response, *args, **kwargs):

        yield from self._get_follow(response, self._css_selectors["pagination"], self.brand_parse)

        yield from self._get_follow(response, self._css_selectors["car"], self.car_parse)

    def car_parse(self, response):
        title = response.css(".AdvertCard_advertTitle__1S1Ak::text").extract_first()
        price = float(response.css("div.AdvertCard_price__3dDCr::text").get().replace("\u2009", ""))
        car_qual = {}
        for qual in response.css("div.AdvertCard_specs__2FEHc .AdvertSpecs_row__ljPcX"):
            type_qual = qual.css(".AdvertSpecs_label__2JHnS::text").extract_first()
            car_qual[type_qual] = qual.css(".AdvertSpecs_data__xK2Qx::text").extract_first() or \
                                  qual.css(".AdvertSpecs_data__xK2Qx a::text").extract_first()

        owner = self._get_author_id(response)
        discr = response.css(".AdvertCard_descriptionInner__KnuRi::text").extract_first()
        photos = [i.attrib.get("src") for i in response.css("figure.PhotoGallery_photo__36e_r img")]
        car = {
            "title": title,
            "trice": price,
            "quality": car_qual,
            "owner": owner,
            "description": discr,
            "photos": photos,
        }
        self.db_client["autoyoula"][self.name].insert_one(car)

    def _get_author_id(self, resp):
        marker = "window.transitState = decodeURIComponent"
        for script in resp.css("script"):
            try:
                if marker in script.css("::text").extract_first():
                    re_pattern = re.compile(r"youlaId%22%2C%22([a-zA-Z|\d]+)%22%2C%22avatar")
                    result = re.findall(re_pattern, script.css("::text").extract_first())
                    return resp.urljoin(f"/user/{result[0]}") if result else None
            except TypeError:
                pass


