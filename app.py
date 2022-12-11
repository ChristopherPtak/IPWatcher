
import json
import re
import requests
import time

from email.mime.text import MIMEText
from smtplib import SMTP


class IPWatcher:

    DATA_DIRECTORY = 'data'
    SMTP_FILENAME = DATA_DIRECTORY + '/smtp.json'
    IP_FILENAME = DATA_DIRECTORY + '/ip.json'

    def __init__(self):
        self._load_data()

    def _load_data(self):
        try:
            with open(IPWatcher.SMTP_FILENAME, 'r') as smtp_file:
                data = json.load(smtp_file)
            self.server   = data['server']
            self.username = data['username']
            self.password = data['password']
            self.sender   = data['sender']
            self.reciever = data['reciever']
        except FileNotFoundError:
            self.server   = input('SMTP Server: ')
            self.username = input('SMTP Username: ')
            self.password = input('SMTP Password: ')
            self.sender   = input('Sender Address (where you want to send the alert from): ')
            self.reciever = input('Reciever Address (where you want to recieve the alert): ')
            with open(IPWatcher.DATA_FILENAME, 'w') as data_file:
                json.dump({
                    'server':   self.server,
                    'username': self.username,
                    'password': self.password,
                    'sender':   self.sender,
                    'reciever': self.reciever
                }, data_file)

        try:
            with open(IPWatcher.IP_FILENAME, 'r') as ip_file:
                data = json.load(ip_file)
                self.ip_address = data.get('ip_address', None)
        except FileNotFoundError:
            self.ip_address = None

    def _dump_data(self):
        with open(IPWatcher.IP_FILENAME, 'w') as ip_file:
            json.dump({'ip_address': self.ip_address}, ip_file)

    def _get_current_ip(self):
        API_URL = 'https://api.ipify.org'
        ip_address = requests.get(API_URL).content.decode('utf-8')
        if re.fullmatch(r'[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+', ip_address):
            return ip_address
        else:
            raise RuntimeError('Could not fetch IP')

    def _send_email(self, subject, content):
        message = MIMEText(content)
        message['Content-Type'] = 'text/html'
        message['Subject']      = subject
        message['To']           = self.reciever
        message['From']         = self.sender

        with SMTP(self.server) as smtp:
            smtp.starttls()
            smtp.login(self.username, self.password)
            smtp.sendmail(self.sender, self.reciever, message.as_string())

    def _send_first_run_alert(self, ip_address):
        lines = [
            '<p>Started watching your IP for changes.</p>',
            f'<p>Your IP address is: <em>{ip_address}</em></p>',
            '<p><small>This alert brought to you by IPWatcher</small></p>'
        ]
        self._send_email('IPWatcher Started', '\n'.join(lines))

    def _send_ip_change_alert(self, old_address, new_address):
        lines = [
            f'<p>Your old IP address was: <em>{old_address}</em></p>',
            f'<p>Your new IP address is: <em>{new_address}</em></p>',
            '<p><small>This alert brought to you by IPWatcher</small></p>'
        ]
        self._send_email('IP Address Changed', '\n'.join(lines))

    def check_for_ip_change(self):
        previous_ip = self.ip_address
        try:
            current_ip = self._get_current_ip()
        except RuntimeError:
            return

        if current_ip != previous_ip:
            self.ip_address = current_ip

        if previous_ip is None:
            self._send_first_run_alert(current_ip)
            self._dump_data()
        elif current_ip != previous_ip:
            self._send_ip_change_alert(previous_ip, current_ip)
            self._dump_data()

if __name__ == '__main__':
    watcher = IPWatcher()
    while True:
        watcher.check_for_ip_change()
        time.sleep(3600)

