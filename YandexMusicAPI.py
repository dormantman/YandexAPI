#! /usr/bin/env python
# -*- coding: utf-8 -*-

#
#      Yandex Music API
#
#    This version: 0.1.0a
#
#       Author: DormantMan
#


import json
from pprint import pprint

import bs4

from Yandex import Yandex


class YandexMusicAPI(Yandex):
    def music(self):
        url = 'https://music.yandex.ru/home'
        response = self.s.get(url)
        soup = bs4.BeautifulSoup(response.content, 'lxml')
        js_data = soup.findAll('script')[1].text.replace('var Mu=', '').rstrip(';')
        pprint(json.loads(js_data))


if __name__ == '__main__':
    api = YandexMusicAPI(user=False)
    api.auth('login', 'password')
    api.music()
