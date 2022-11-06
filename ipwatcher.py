
import json
import requests
import time

from email.mime.text import MIMEText
from smtplib import SMTP


class IPWatcher:

    DATA_FILENAME = 'ipwatcher.data.json'

    def __init__(self):
        self._load_data()

    def _load_data(self):
        try:
            with open(IPWatcher.DATA_FILENAME, 'r') as data_file:
                data = json.load(data_file)
        except FileNotFoundError:
            data = {}

        def get_or_ask(key, prompt):
            if key in data:
                return data[key]
            else:
                return input(prompt)

        self.server     = get_or_ask('server',   'SMTP Server: ')
        self.username   = get_or_ask('username', 'SMTP Username: ')
        self.password   = get_or_ask('password', 'SMTP Password: ')
        self.sender     = get_or_ask('sender',   'Sender Address (where you want to send the alert from): ')
        self.reciever   = get_or_ask('reciever', 'Reciever Address (where you want to recieve the alert): ')
        self.ip_address = data.get('ip_address', None)

    def _dump_data(self):
        with open(IPWatcher.DATA_FILENAME, 'w') as data_file:
            json.dump({
                'server':     self.server,
                'username':   self.username,
                'password':   self.password,
                'sender':     self.sender,
                'reciever':   self.reciever,
                'ip_address': self.ip_address
            }, data_file)

    def _get_current_ip(self):
        API_URL = 'https://api.ipify.org'
        return requests.get(API_URL).content.decode('utf-8')

    def _send_ip_change_alert(self, old_address, new_address):
        lines = [
            f'<p>Your old IP address was: <em>{old_address}</em></p>',
            f'<p>Your new IP address is: <em>{new_address}</em></p>',
            '<p><small>This alert brought to you by IPWatcher</small></p>'
        ] 

        message = MIMEText('\n'.join(lines))
        message['Content-Type'] = 'text/html'
        message['Subject']      = 'IP Address Changed'
        message['To']           = self.reciever
        message['From']         = self.sender

        with SMTP(self.server) as smtp:
            smtp.starttls()
            smtp.login(self.username, self.password)
            smtp.sendmail(self.sender, self.reciever, message.as_string())

    def check_for_ip_change(self):
        previous_ip = self.ip_address
        current_ip = self._get_current_ip()

        if current_ip != previous_ip:
            self._send_ip_change_alert(previous_ip, current_ip)
            self.ip_address = current_ip
            self._dump_data()

if __name__ == '__main__':
    watcher = IPWatcher()
    while True:
        watcher.check_for_ip_change()
        time.sleep(3600)

