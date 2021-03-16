import os
from dotenv import load_dotenv
from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from gb_parse.spiders.users_instagram import UsersInstagramSpider

if __name__ == '__main__':
    load_dotenv(".env")
    crawler_settings = Settings()
    crawler_settings.setmodule('gb_parse.settings')
    crawler_process = CrawlerProcess(settings=crawler_settings)
    crawler_process.crawl(UsersInstagramSpider,
                          login=os.getenv('INST_LOGIN'),
                          enc_password=os.getenv('INST_PASSWORD'),
                          start_user='goblin_oper',
                          end_user='serebro_tomsk70')
    crawler_process.start()