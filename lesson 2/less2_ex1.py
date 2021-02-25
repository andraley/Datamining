import requests
from urllib.parse import urljoin
import bs4
import pymongo
import datetime as dt


class MagnitParse:
    """
    Париснг акционных товаров у магнита
    """

    def __init__(self, start_url: str, db_client: pymongo):
        self.start_url = start_url
        self.db = db_client["datamining"]

    def _get_response(self, url: str):
        """
        Получает данные с сайта
        :param url: str
        :return:
        """
        for i in range(5):
            response = requests.get(url)
            if response.status_code == 200:
                return response
            sleep(1+i)
        raise ValueError('Нет ответа от сайта')

    def _get_soup(self, url: str):
        """
        Переводить html данные soup
        :param url: str
        :return:
        """
        response = self._get_response(url)
        soup = bs4.BeautifulSoup(response.text, "lxml")
        return soup

    def _change_date(self, date: str):
        """
        Переводить стройчуту дату в форсат datatime
        :param date:
        :return:
        """
        month = {
            "янв": 1,
            "фев": 2,
            "мар": 3,
            "апр": 4,
            "май": 5,
            "июн": 6,
            "июл": 7,
            "авг": 8,
            "сен": 9,
            "окт": 10,
            "ноя": 11,
            "дек": 12,
        }

        list_date = date.split()
        start_date = dt.datetime(
                                 year=dt.datetime.now().year,
                                 month=month[list_date[2][:3]],
                                 day=int(list_date[1]),
                                )
        try:
            end_date = dt.datetime(
                                    year=dt.datetime.now().year,
                                    month=month[list_date[5][:3]],
                                    day=int(list_date[4]),
                                  )
        except IndexError:
            end_date = start_date
            start_date = None
        return start_date, end_date

    def _change_price(self, price: str):
        """
        Переводит цену в чистовой формат
        :param price:
        :return:
        """
        list_price = price.split()
        try:
            int(list_price[0])
        except ValueError:
            return None
        str_price = f"{list_price[0]}.{list_price[1]}"
        price = float(str_price)
        return price

    def _template(self):
        """
        Организовывает словарь из данных
        :return:
        """
        return {
            "url": lambda a: urljoin(self.start_url, a.attrs.get("href")),
            "promo_name": lambda a: a.find("div", attrs={"class": "card-sale__header"}).text,
            "product_name": lambda a: a.find("div", attrs={"class": "card-sale__title"}).text,
            "old_price": lambda a: self._change_price(a.find("div", attrs={"label__price label__price_old"}).text),
            "new_price": lambda a: self._change_price(a.find("div", attrs={"label__price label__price_new"}).text),
            "image_url": lambda a: urljoin(self.start_url, a.find("img").attrs.get("data-src")),
            "date_from": lambda a: self._change_date(a.find("div", attrs={"class": "card-sale__date"}).text)[0],
            "date_to": lambda a: self._change_date(a.find("div", attrs={"class": "card-sale__date"}).text)[1],
        }

    def run(self):
        """
        Запуск парсера
        :return:
        """
        soup = self._get_soup(self.start_url)
        catalog = soup.find("div", attrs={"class": "сatalogue__main"})
        for product_a in catalog.find_all("a", recursive=False):
            product_data = self._parse(product_a)
            if product_data.get("product_name") is None:
                continue
            self._save(product_data)

    def _parse(self, product_a: bs4.Tag) -> dict:
        """
        Переводить данные из soup в словарь
        :param product_a:
        :return:
        """
        product_data = {}
        for key, funk in self._template().items():
            try:
                product_data[key] = funk(product_a)
            except AttributeError:
                pass
        return product_data

    def _save(self, data: dict):
        """
        Сохраняет данные в базу
        :param data:
        :return:
        """
        collection = self.db["magnit"]
        collection.insert_one(data)


if __name__ == "__main__":
    url = "https://magnit.ru/promo/"
    db_client = pymongo.MongoClient("mongodb://localhost:27017")
    parser = MagnitParse(url, db_client)
    parser.run()
