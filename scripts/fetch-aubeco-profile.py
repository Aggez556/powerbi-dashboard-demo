"""Download public brand evidence and the latest Microsoft report-theme schema."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.request import Request, urlopen
from urllib.parse import urljoin
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[1]
BASE = 'https://www.aubeco.se/'
entries = []

def fetch(url, relative):
    with urlopen(Request(url, headers={'User-Agent': 'Aubeco-profile-analysis/1.0'}), timeout=40) as response:
        data = response.read()
        entry = {'url': url, 'resolved_url': response.url, 'file': relative,
                 'content_type': response.headers.get('Content-Type'),
                 'sha256': hashlib.sha256(data).hexdigest()}
    target = ROOT / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)
    entries.append(entry)
    return data

class Assets(HTMLParser):
    def __init__(self):
        super().__init__()
        self.css = []
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'link' and attrs.get('rel') == 'stylesheet':
            self.css.append(urljoin(BASE, attrs['href']))

html = fetch(BASE, 'assets/aubeco/sources/home.html').decode('utf-8')
parser = Assets()
parser.feed(html)
for url in parser.css:
    filename = url.rsplit('/', 1)[-1]
    css = fetch(url, f'assets/aubeco/sources/{filename}').decode('utf-8')
    (ROOT / f'assets/aubeco/sources/{filename}.readable.txt').write_text(css.replace('}', '}\n'), encoding='utf-8')
fetch(urljoin(BASE, 'aubeco-google-bild.png'), 'assets/aubeco/aubeco-original.png')
fetch(urljoin(BASE, 'favicon.png'), 'assets/aubeco/favicon-original.png')
api = 'https://api.github.com/repos/microsoft/powerbi-desktop-samples/contents/Report%20Theme%20JSON%20Schema'
files = json.loads(fetch(api, 'themes/schema/catalog.json'))
schemas = [f for f in files if re.fullmatch(r'reportThemeSchema-\d+\.\d+\.json', f['name'])]
latest = max(schemas, key=lambda f: tuple(map(int, re.findall(r'\d+', f['name']))))
fetch(latest['download_url'], 'themes/schema/' + latest['name'])
(ROOT / 'assets/aubeco/sources/manifest.json').write_text(json.dumps({'retrieved_date': '2026-10-06', 'entries': entries}, indent=2), encoding='utf-8')
print('CSS:', parser.css)
print('Schema:', latest['name'])
