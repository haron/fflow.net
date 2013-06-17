import re
import requests
from flask import Flask, request, render_template
from BeautifulSoup import BeautifulSoup
from PIL import Image
from StringIO import StringIO

app = Flask(__name__)
app.debug = True
log = app.logger

FEED_PROXY = 'http://ajax.googleapis.com/ajax/services/feed/load'
MAX_ITEMS = 10
TN_WIDTH = 500
TN_HEIGHT = 170

slug_pattern = re.compile(r'[^\w\d\-/]+')
youtube_pat = re.compile(r'.*youtube.com/v/([\w\d_-]+).*')
vimeo_pat = re.compile(r'.*vimeo\.com/moogaloop\.swf\?clip_id=(\d+).*')

@app.route('/feed/')
def feed():
    feed_url = request.args.get('url', None)
    feed = process(feed_url)
    return (render_template("feed.xml", **feed), 200, {"Content-Type": "text/xml; charset=utf-8"})

def fetch_json(url, params):
    return requests.get(url, params=params).json()

def process(url):
    params = {
            'v': '1.0',
            'q': url,
            'num': MAX_ITEMS,
            }
    resp = requests.get(FEED_PROXY, params=params).json()
    feed = resp['responseData']['feed']
    feed['items'] = []
    for entry in feed['entries']:
        entry = Item(**entry)
        feed['items'].append(entry)
    return feed

class Item(object):
    thumbnail = None

    def __init__(self, *args, **kwargs):
        if not 'guid' in kwargs:
            kwargs['guid'] = kwargs['link']
        for k in kwargs:
            self.__dict__[k] = kwargs[k]
        self.process()

    def __str__(self):
        return '<Item: %s>' % self.link

    def process(self):
        log.info('Processing %s' % self)
        self.html = BeautifulSoup(self.content)
        media_tn = None

        images = self.html.findAll('img')
        for i in images:
            log.debug(i)
            width, height = Image.open(StringIO(requests.get(i["src"]).content)).size
            if width >=50 and height >= 50:
                tn_width, tn_height = tn_size(width, height)
                self.thumbnail = {
                        "url": i["src"],
                        "get_url": i["src"],
                        "width": tn_width,
                        "height": tn_height
                        }
                break
        return

def tn_size(width, height):
    if float(width) / TN_WIDTH > float(height) / TN_HEIGHT:
        ratio = float(TN_WIDTH) / width
    else:
        ratio = float(TN_HEIGHT) / height
    width = int(width * ratio)
    height = int(height * ratio)
    return width, height

def main():
    app.run(host="0.0.0.0")

if __name__ == '__main__':
    main()

