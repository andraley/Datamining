# Задача организовать сбор данных,
# необходимо иметь метод сохранения данных в .json файлы
#
# результат: Данные скачиваются с источника, при вызове
# метода/функции сохранения в файл скачанные данные сохраняются
# в Json вайлы, для каждой категории товаров должен быть создан
# отдельный файл и содержать товары исключительно соответсвующие
# данной категории.
#
# пример структуры данных для файла:
#
# {
# "name": "имя категории",
# "code": "Код соответсвующий категории (используется в запросах)",
# "products": [{PRODUCT},  {PRODUCT}........] # список словарей
# товаров соответсвующих данной категории
# }

import requests
import json
from pathlib import Path
from time import sleep


class Parse5:
    """
    Класс для парсеринга товаров по акции из Петёрочки
    """
    headers = {
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:85.0)"
                      "Gecko/20100101 Firefox/85.0",
    }

    def __init__(self, cat_url: str, prod_url: str, cat_path: Path):
        self.cat_url = cat_url
        self.prod_url = prod_url
        self.cat_path = cat_path

    def _get_cat(self, url_cat: str):
        """
        Получение катагорий
        :param url_cat: str
        :return:
        """
        for i in range(5):
            cat_json = requests.get(url_cat, headers=self.headers)
            if cat_json.status_code == 200:
                return cat_json
            sleep(1+i)
        raise ValueError('Нет ответа от сайта')

    def _get_prod(self, url_prod: str, cat: str):
        """
        Получение товаров
        :param url_prod: str
        :return:
        """
        params = {"categories": cat}

        for i in range(5):
            prod_json = requests.get(url_prod, params=params,
                                     headers=self.headers)
            if prod_json.status_code == 200:
                return prod_json
            sleep(1+i)
        raise ValueError('Нет ответа от сайта')

    def _to_dict(self, url_cat: str, url_prod: str) -> dict:
        """
        Собирает словарь из json данных
        :param url_cat: str
        :param url_prod: str
        :return: dict
        """
        cat_json = self._get_cat(url_cat)
        cat_list = cat_json.json()
        cat_prod_dict = {}

        for cat in cat_list:
            prod_dict = []
            url = url_prod
            while url:
                prod_json = self._get_prod(url, cat["parent_group_code"])
                prod_list = prod_json.json()
                url = prod_list["next"]
                for prod in prod_list["results"]:
                    prod_dict.append(prod)
            cat_prod_dict["name"] = cat["parent_group_name"]
            cat_prod_dict["code"] = cat["parent_group_code"]
            cat_prod_dict["products"] = prod_dict
            yield cat_prod_dict

    def parse(self):
        """
        Записывает в файл полученые данные
        :return:
        """
        for cat in self._to_dict(self.cat_url, self.prod_url):
            cat_path = self.cat_path.joinpath(f"{cat['code']}.json")
            data_json = json.dumps(cat, ensure_ascii=False)
            cat_path.write_text(data_json, encoding="UTF-8")


if __name__ == "__main__":
    url_prod = "https://5ka.ru/api/v2/special_offers/"
    url_cat = "https://5ka.ru/api/v2/categories/"

    save_path = Path(__file__).parent.joinpath("categories")
    if not save_path.exists():
        save_path.mkdir()

    parser = Parse5(url_cat, url_prod, save_path)
    parser.parse()
