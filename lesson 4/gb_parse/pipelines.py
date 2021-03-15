# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from scrapy import Request
from scrapy.pipelines.images import ImagesPipeline
import pymongo


class MongoPipeline:
    def __init__(self):
        self.db = pymongo.MongoClient()["gb_db"]

    def process_item(self, item, spider):
        if not self.db[item.__class__.__name__].count({"url": item["url"]}):
            self.db[item.__class__.__name__].insert_one(item)
        return item


class GbImagePipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        for img_url in item.get("images", []):
            yield Request(img_url)

    def item_completed(self, results, item, info):
        item["images"] = [itm[1] for itm in results]
        return item