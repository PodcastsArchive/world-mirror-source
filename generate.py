from html import entities
import shutil
import feedparser
from datetime import datetime
import pathlib
import urllib.request
import os
import re

URL = os.getenv('RSS_URL')
if URL == '':
    raise "no rss url."

ONLINE_PREFIX = 'https://podcastsarchive.github.io/worlds-mirror'
IMG_URL = 'https://podcastsarchive.github.io/worlds-mirror/image/img.jpg'
AUTHOR = ' wqj '

feed = feedparser.parse(URL)
all_entries = feed['entries']
image_url = feed['feed']['image']['href']
print(image_url)
entries_len = len(all_entries)
entries = all_entries
# entries = all_entries[:entries_len - audio_len]

print(f'new entries {len(entries)}')
print(f'loading podcast from {URL}')

size = index = entries_len
index = size
playlist_items = []

if not os.path.exists("./source/_posts/"):
    os.makedirs("./source/_posts/")

if image_url:
    # download new image.
    urllib.request.urlretrieve(image_url, './new_img.jpg')
    shutil.copyfile('./new_img.jpg', './img.jpg')
    shutil.copyfile('./new_img.jpg', './source/image/img.jpg')
    os.remove('./new_img.jpg')

shutil.copyfile('./_config.yml', './themes/Chic/_config.yml')

def replace_archer(u):
    if u is None:
        return u.group()
    g = sum([int(s) * 60 ** abs(index) for index, s in enumerate(u.group().split(':')[::-1])])
    return f'{{% playertime {u.group()} {g} %}}'   

# Generate All Items.
for entry in entries:
    title = entry['title'].replace('"', '')
    date = entry['published']
    date = datetime.strptime(date, "%a, %d %b %Y %H:%M:%S GMT")
    date = date.strftime('%Y-%m-%d %H:%M:%S')
    audio = entry['links'][0]['href']
    detail = entry['title_detail']
    player = '{% aplayer ' + f'"{title}"' + AUTHOR + ' ' + audio + ' ' + IMG_URL + ' %}'
    summary = entry['summary']
    summary = re.sub('style=\".*?\"', '', summary)
    summary = re.sub(r'\d+\:\d+((\:\d+)?)', replace_archer, summary)
    durnation = entry['itunes_duration']
    length = entry['links'][0]['length']
    playlist_items.append( f'{{"title": "{title}", "author": "{AUTHOR}", "url": "{audio}", "pic": "{IMG_URL}"}}')
    md_builder = \
    f'''---
title: "{title}"
date: {date}
duration: '{ durnation }'
media: { audio }
image: { IMG_URL }
length: { length }
type: 'audio/mpeg'
---

{player}

**[Link]({entry['links'][1]['href']})**

## Summary
{summary}
    '''

    pathlib.Path(f'source/_posts/vol{index}.md').write_text(md_builder)
    print(f'generate md file for source/_posts/vol{index}.md')
    index -= 1

# Generate Play List
playlist = \
f'''---
title: "PlayList"
---
{{% aplayerlist %}}
{{
    "narrow": false,
    "autoplay": false,
    "mode": "order",
    "mutex": true,
    "preload": "auto",
    "listmaxheight": "1000px",
    "music": [{','.join(playlist_items)}]
}}
{{% endaplayerlist %}}

'''
pathlib.Path(f'source/playlist.md').write_text(playlist)
