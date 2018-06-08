#! /usr/bin/env python
# -*- coding: utf-8 -*-

#
#      Yandex
#
#    This version: 0.1.0a
#
#       Author: DormantMan
#


import os
import pickle
from getpass import getpass

import bs4
import requests


class Yandex:
    version = '0.1.0a'

    def __init__(self, user=False):
        print('Yandex %s' % self.version)

        self.s = requests.session()
        self.s.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0'
        }

        self.profile = {
            'first_name': None,
            'last_name': None,
            'username': None,
        }
        self.form = {
            'username': None,
            'password': None,
        }
        self.login = False

        self.cookies_path = os.path.join('.dm', 'cookies.dm')

        if not os.access('.dm', os.F_OK):
            os.mkdir('.dm')

        self.load_cookies(self.cookies_path)

        if not self.get_status() and user:
            username = input('Username: ')
            password = getpass('Password: ')

            if self.auth(username, password):
                self.save_cookies(self.cookies_path)

    def get_status(self):
        return self.login

    def auth(self, login, password):
        self.form = {
            'username': login,
            'password': password,
        }

        if self.login:
            print('You are already authorized.')
            return True

        url = 'https://passport.yandex.ru/auth'

        self.s.post(url, data={'login': self.form['username'], 'passwd': self.form['password'], })

        response = self.s.get('https://passport.yandex.ru/profile/')
        soup = bs4.BeautifulSoup(response.content, "lxml")

        if soup.find('div', {'class': 'personal-info-name'}):
            print('Successful authorization!')

            self.load_profile_info(content=response.content)
            self.login = True
            self.save_cookies(self.cookies_path)

        else:
            print('^^^ Wrong login or password! ^^^')

        return self.login

    def logout(self):
        self.s = requests.session()
        self.s.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0'
        }
        self.profile = {
            'first_name': None,
            'last_name': None,
            'username': None,
        }
        self.login = False

    def load_profile_info(self, content=None):
        if content is None:
            response = self.s.get('https://passport.yandex.ru/profile/')
            content = response.content

        soup = bs4.BeautifulSoup(content, "lxml")

        self.profile = {
            'first_name': soup.find('div', {'data-reactid': 72}).text,
            'last_name': soup.find('div', {'data-reactid': 73}).text,
            'username': soup.find('div', {'data-reactid': 74}).text,
        }

        return self.profile

    def save_cookies(self, filename):
        print('Save cookies ...')
        try:
            with open(filename, 'wb') as cookies:
                pickle.dump(self.s.cookies, cookies)
        except IOError:
            print('^^^ Error save cookies ^^^')

    def load_cookies(self, filename):
        print('Loading cookies ...')

        try:
            with open(filename, 'rb') as f:
                self.s.cookies = pickle.load(f)

        except IOError:
            pass

        response = self.s.get('https://passport.yandex.ru/profile/')
        soup = bs4.BeautifulSoup(response.content, "lxml")

        if soup.find('div', {'class': 'personal-info-name'}):
            print('Cookies loaded : OK')

            self.load_profile_info(content=response.content)
            self.login = True
            self.save_cookies(self.cookies_path)

        else:
            print('Cookies not loaded : BAD')

        return self.login


if __name__ == '__main__':
    yandex = Yandex(user=False)
    yandex.auth('login', 'password')
    print(yandex.profile)
