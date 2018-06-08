#! /usr/bin/env python
# -*- coding: utf-8 -*-

#
#      Yandex Mail API
#
#    This version: 0.1.0a
#
#       Author: DormantMan
#

import base64
import email
import imaplib
import os
import pickle
import quopri
import time
import webbrowser

from Yandex import Yandex


class YandexMailAPI(Yandex):
    def __init__(self, user=False):
        super().__init__(user=user)

        self.server = 'imap.yandex.ru'
        print("Connecting to {}...".format(self.server))
        self.mail = imaplib.IMAP4_SSL(self.server)

    def auth(self, login, password):
        self.form = {
            'username': login,
            'password': password,
        }

        if self.login:
            print('You are already authorized.')
            return True

        print("Connected! Logging in as {}...".format(self.form['username']))

        try:
            status, msg = self.mail.login(
                self.form['username'],
                self.form['password']
            )

        except Exception as error:
            status, msg = 'ERROR', error.args

        print(status, msg[0].decode(), sep=' | ')

        self.login = status == 'OK'

    def load_cookies(self, filename):
        print('Loading cookies ...')

        try:
            with open(filename, 'rb') as f:
                self.s.cookies = pickle.load(f)

        except IOError:
            pass

        return False

    def inbox(self, json_format=False):
        if not self.login:
            return 'You are not authorized.'

        status, msg = self.mail.select('INBOX')

        if json_format:
            return {'number': int(msg[0].decode())}
        return 'Number of incoming messages: %s' % msg[0].decode()

    def letter(self, msg_id, auto_open=True, filename=os.path.join('.dm', 'letter.mail.html')):
        if not self.login:
            return print('You are not authorized.')

        if msg_id < 0:
            msg_id = self.inbox(json_format=True)['number'] + msg_id + 1
        elif msg_id == 0:
            return print('No letter with a zero index :)')

        status, data = self.mail.fetch(msg_id.__str__().encode(), '(RFC822)')
        msg = email.message_from_bytes(data[0][1], _class=email.message.EmailMessage)

        sender = email.header.decode_header(msg['From'])[0][0]
        subject = email.header.decode_header(msg['Subject'])[0][0]
        to = email.header.decode_header(msg['To'])[0][0]

        try:
            if type(sender) == bytes:
                sender = sender.decode()
            if type(subject) == bytes:
                subject = subject.decode()
            if type(to) == bytes:
                to = to.decode()

        except UnicodeDecodeError:
            pass

        print()
        print('FROM: {sender} [{email}]'.format(sender=sender, email=msg['Return-Path']))
        print('TO: {email}'.format(email=to))
        print('Subject: {subject} [{date}]'.format(subject=subject, date=msg['Date']))
        print()

        # print('\n', msg['Received'], '\n') # DEBUG

        payload = msg.get_payload()
        while type(payload) == list:
            msg = payload[-1]
            payload = msg.get_payload()

        encoding = msg['Content-Transfer-Encoding']
        print('-*- Encoding: {encoding} -*-'.format(encoding=encoding))

        if encoding == 'quoted-printable':
            body = quopri.decodestring(payload)
        elif encoding == 'base64':
            body = base64.b64decode(payload)
        else:
            if type(payload) == str:
                body = payload.encode()
            else:
                body = payload.get_payload().encode()

        print('Save HTML to "{filename}" ...'.format(filename=filename))

        with open(filename, 'wb') as file:
            file.write(body)

        return webbrowser.open_new_tab(filename) if auto_open else None

    def loop(self):
        for i in range(1, self.inbox(json_format=True)):
            api.letter(-i)
            time.sleep(3)

    def logout(self):
        status, msg = self.mail.logout()
        print(status, msg[0].decode(), sep=' | ')


if __name__ == '__main__':
    api = YandexMailAPI()
    api.auth('login', 'password')
    print(api.inbox())
    api.letter(-1)
    api.logout()
