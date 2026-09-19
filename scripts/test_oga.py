import requests
import re

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
r = requests.get('https://opengameart.org/content/town-theme-rpg', headers=headers)
matches = re.findall(r'https://opengameart\.org/sites/default/files/[^"\']+\.(?:mp3|ogg|wav)', r.text)
print("Files found:", matches)
