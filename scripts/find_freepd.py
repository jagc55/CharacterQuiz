import requests
import re

headers = {'User-Agent': 'Mozilla/5.0'}
for category in ['electronic', 'misc', 'upbeat']:
    url = f'https://freepd.com/{category}.php'
    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        matches = re.findall(r'href="([^"]+\.mp3)"', r.text)
        print(f'{category} tracks found: {len(matches)}')
        for m in matches[:8]:
            print(' ', m)
