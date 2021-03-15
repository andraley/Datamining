import os
import dotenv
from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from gb_parse.spiders.instagram import InstagramSpider


if __name__ == '__main__':
    dotenv.load_dotenv('.env')
    crawler_settings = Settings()
    crawler_settings.setmodule('gb_parse.settings')
    crawler_process = CrawlerProcess(settings=crawler_settings)
    crawler_process.crawl(InstagramSpider, login=os.getenv('INST_LOGIN'), password=os.getenv('INST_PASSWORD'))
    crawler_process.start()