import requests
import re
from pathlib import Path

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

urls = [
    'https://opengameart.org/content/audio-cc0-8bit-chiptune',
    'https://opengameart.org/content/cc0-retro-music',
    'https://opengameart.org/content/chill-chiptune'
]

found_links = set()
for u in urls:
    try:
        r = requests.get(u, headers=headers, timeout=8)
        # Find content links
        node_links = re.findall(r'href="(/content/[^"]+)"', r.text)
        print(f"Found {len(node_links)} content links on {u.split('/')[-1]}")
        for nl in node_links[:15]:
            full_nl = "https://opengameart.org" + nl
            r_node = requests.get(full_nl, headers=headers, timeout=6)
            # Check if CC0 is in page text
            if "CC0" in r_node.text or "Public Domain" in r_node.text:
                audio_files = re.findall(r'href="(https://opengameart\.org/sites/default/files/[^"]+\.(?:mp3|ogg|wav))"', r_node.text)
                for af in audio_files:
                    found_links.add((nl.split('/')[-1], af))
                    print(f"  [CC0 Audio] {nl.split('/')[-1]} -> {af}")
    except Exception as e:
        print(f"Error {u}: {e}")

print(f"Total verified CC0 tracks found: {len(found_links)}")
