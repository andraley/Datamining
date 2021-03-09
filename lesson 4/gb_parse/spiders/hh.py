import scrapy
from gb_parse.loaders import HHLoader

pages = {
    "pagination": '//div[@data-qa="pager-block"]//a[@data-qa="pager-page"]/@href',
    "vacancy": '//div[contains(@data-qa, "vacancy-serp__vacancy")]//'
    'a[@data-qa="vacancy-serp__vacancy-title"]/@href',
}

jobs = {
    "title": '//h1[@data-qa="vacancy-title"]/text()',
    "salary": '//p[@class="vacancy-salary"]/span/text()',
    "description": '//div[@data-qa="vacancy-description"]//text()',
    "skills": '//div[@class="bloko-tag-list"]//'
    'div[contains(@data-qa, "skills-element")]/'
    'span[@data-qa="bloko-tag__text"]/text()',
    "author": '//a[@data-qa="vacancy-company-name"]/@href',
}

companies = {
    "company_name": '//h1[@class="bloko-header-1"]/span/text()',
    "site": '//div[@class="employer-sidebar-content"]/a[@data-qa="sidebar-company-site"]/@href',
    "business": '//div[@class="employer-sidebar-content"]/p/text()'.split(sep=','),
}


class HhSpider(scrapy.Spider):
    name = "hh"
    allowed_domains = ["hh.ru"]
    start_urls = [
        "https://spb.hh.ru/search/vacancy?schedule=remote&L_profession_id=0&area=113"
    ]

    def _get_follow_xpath(self, response, xpath, callback):
        for url in response.xpath(xpath):
            yield response.follow(url, callback=callback)

    def parse(self, response):
        callbacks = {"pagination": self.parse, "vacancy": self.vacancy_parse}

        for key, xpath in pages.items():
            yield from self._get_follow_xpath(response, xpath, callbacks[key])

    def vacancy_parse(self, response):
        loader = HHLoader(response=response)
        loader.add_value("url", response.url)
        for key, xpath in jobs.items():
            loader.add_xpath(key, xpath)
            self._get_follow_xpath(response, jobs['author'], self.company_parse)
        yield loader.load_item()

    def company_parse(self, response):
        loader = HHLoader(response=response)
        for key, xpath in companies.items():
            loader.add_xpath(key, xpath)
        yield loader.load_item()
