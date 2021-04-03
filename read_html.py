# coding=gbk
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
import urllib.request
from urllib.parse import (urlparse, urlunparse)
from urllib.request import (urlopen, urlretrieve)
import codecs
import os
import json
from PIL import Image
import PIL
import glob

with os.scandir("html/") as entries:
    for e in entries:
        if e.name.endswith('.html'):
            file = codecs.open(e, "r", "utf-8")
            html = file.read()
            soup = BeautifulSoup(html, "html.parser")

            data = []

            for l in soup.findAll('span',{"data-type":"bbsline"}):
                l2 = l.findAll('span')

                id = ''
                ext1 = ''
                name = ''
                type = ''
                caption = ''
                hot = ''
                manager = ''

                if(len(l2)>4):
                    if('getPointer' in l2[1].getText()):
                        a = l2[1].getText().split("}}")[1]
                        b = ' '.join(a.split()).split(' ')
                        if(len(b)>1):
                            id = b[0]
                            name = b[1]
                            type = l2[2].getText()
                            caption = l2[3].getText()
                            c = ' '.join(caption.split()).split(' ')
                            if(c[len(c)-2].isnumeric()):
                                hot = c[len(c)-2]
                            else:
                                hot = ''
                            manager = c[len(c)-1]

                        else:
                            id = a;
                            name = l2[3].getText()
                            type = l2[4].getText()
                            caption = l2[5].getText()
                            c = ' '.join(caption.split()).split(' ')
                            if (c[len(c) - 2].isnumeric()):
                                hot = c[len(c) - 2]
                            else:
                                hot = ''
                            manager = c[len(c) - 1]


                        # 48   TribalWars   線上 ◎Tribalwars 一年一度，新年快樂        nekaki
                        if('q15' in l2[2].get('class')):
                            ext1 = ''
                        elif('q11' in l2[2].get('class')):
                            print()
                        # 50 ˇVALORANT     線上 ◎[VALORANT] 瓦羅蘭 特 戰英豪          zhtw/rainnaw
                        else:
                            ext1 = l2[2].getText()

                        item = {'id': str(id),
                                'ext1': ext1,
                                'name': name.strip(),
                                'type': type.strip(),
                                'caption': caption,
                                'hot': hot,
                                'manager': manager}
                        print(item)
                        data.append(item)


                elif(len(l2)>5):
                    print("hey")


            print("done")
            dumped = []
            for d in data:
                dumped.append(d)
            out = json.dumps(dumped, indent=4,ensure_ascii=False)
            with open("html/" + 'result.json', 'w', encoding='utf-8') as f:
                f.write(out)