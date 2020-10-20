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

home = {}
db = []


def find_id_by_name(name):
    for i in db:
        if i['name'] == name:
            # print(name + " is match with " + i['name'])
            return i['id']
    print('Series '+name+' doesnt have db pointer')
    return None


if __name__ == "__main__":
    with open('home.json', 'r', encoding='utf-8') as f:
        home = json.load(f)

    with open('db.json', 'r', encoding='utf-8') as f:
        db = json.load(f)

    for h in home:
        for i in home[h]:
            if ('items' in i):
                for item in i['items']:
                    # print(item)
                    db_id = find_id_by_name(item['name'])
                    item['id'] = str(db_id)
            else:
                # print(i)
                db_id = find_id_by_name(i['name'])
                i['id'] = str(db_id)

    out = json.dumps(home, indent=4, ensure_ascii=False)
    with open('fixed.json', 'w', encoding='utf-8') as f:
        f.write(out)