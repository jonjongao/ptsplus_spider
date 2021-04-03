from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
import urllib.request
from urllib.parse import (urlparse, urlunparse)
from urllib.request import (urlopen, urlretrieve)
import codecs
import os
import json
from PIL import Image
import PIL
import glob
import time
import random


db = []
child = []

rnd_yt=[
    'https://www.youtube.com/embed/_hYJoVpjELg',
    'https://www.youtube.com/embed/aOxheDoks_Y',
    'https://www.youtube.com/embed/LGrpsZ7BsQA'
]


def find_id_by_name(name):
    for i in db:
        if i['name'] == name:
            # print(name + " is match with " + i['name'])
            return i['id']
    print('Series '+name+' doesnt have db pointer')
    return None


if __name__ == "__main__":
    with open('get_child/db.json', 'r', encoding='utf-8') as f:
        db = json.load(f)

    with open('get_child/db2.json', 'r', encoding='utf-8') as f:
        db2 = json.load(f)
        for a in db2:
            db.append(a)

    for h in db:
        if h['parent'] != None or h['parent'] != '':
            item = {'id': h['id'],
                    'yt_url': random.choice(rnd_yt)}
            child.append(item)

    out = json.dumps(child, indent=4, ensure_ascii=False)
    with open('get_child/fixed.json', 'w', encoding='utf-8') as f:
        f.write(out)
    