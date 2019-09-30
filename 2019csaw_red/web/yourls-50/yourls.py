#!/usr/bin/python3

from flask import Flask, request, render_template
from requests import get
from requests.exceptions import InvalidURL
from urlparse import urlparse
import re
import urllib

app=Flask(__name__)


@app.route('/flag')
def flag():
    if request.remote_addr not in ['localhost', '127.0.0.1']:
        return 'request must come from localhost'

    with open('flag.txt') as f:
        return f.read()


@app.route('/', methods=['GET', 'POST'])
def index():

    if request.method == 'POST':
        url = request.form['url'] if 'url' in request.form else None

        if urlparse(url).scheme != 'http':
            return 'http only plz'

        hostname = re.search(
            '(?:http.*://)?(?P<host>[^:/ ]+).?(?P<port>[0-9]*).*',
            url
        ).group('host')

        if hostname in ('localhost', '127.0.0.1', '0.0.0.0'):
            return 'hostname is no bueno (i wont let you request localhost)'

        try:
            res = get(url)
        except InvalidURL:
            return 'that be not a valid url my friend'

        return res.text

    return render_template('index.html')


if __name__ == "__main__":
    app.run(debug=True)