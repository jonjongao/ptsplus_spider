# coding=gbk
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

data_begin_id = 5000
read_path = 'raw/'
output_path = 'out_home/'


class Home:
    carousel = []
    new_recommend = []
    series = []

    def __init__(self):
        self.carousel = []
        self.new_recommend = []
        self.series = []


data = {}
dumped_data = {}
url_length = 0
ignore_file = ['app-store.png', 'google-play.png', 'pts_logo_l.png']


def compress_image():
    print("Start compressing images")
    for entry in os.scandir(output_path):
        if entry.is_dir():
            for e in os.scandir(entry):
                # print(e.path)
                img = Image.open(e.path)
                b_size = os.path.getsize(e.path)
                # print(f"The image size dimensions are: {img.size}")
                # print("size before compress:" + str(b_size))
                if e.name.endswith('.png'):
                    rgb_img = img.convert('RGB')
                    ext = os.path.splitext(e.name)[0] + '.jpg'
                    p = entry.path + "/" + ext
                    rgb_img.save(p, optimize=True, quality=10)
                    a_size = os.path.getsize(p)
                    os.remove(e.path)
                    # print("size after compress:" + str(a_size))
                else:
                    img.save(e.path, optimize=True, quality=10)
                    a_size = os.path.getsize(e.path)
                    # print("size after compress:" + str(a_size))

    print("Done compress")


def reporthook(a, b, c):
    """
    显示下载进度
    :param a: 已经下载的数据块
    :param b: 数据块的大小
    :param c: 远程文件大小
    :return: None
    """
    # print("\rdownloading: %5.1f%%" % (a * b * 100.0 / c), end="")


def on_parse_complate():
    print("is done")
    global dumped_data
    dumped_data = {}
    dumped_data = data.__dict__
    out = json.dumps(dumped_data, indent=4, ensure_ascii=False)
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    # print(out)
    with open(output_path + 'result.json', 'w', encoding='utf-8') as f:
        f.write(out)
    compress_image()


def parse_index(url, html):
    soup = BeautifulSoup(html, "html.parser")


def process_image(url, src, id):
    parsed = list(urlparse(url))
    link = urllib.parse.quote(src, safe=':/')
    filename = os.path.basename(src)
    if filename in ignore_file:
        return
    parsed[2] = link

    if not os.path.exists(output_path + str(id)):
        os.makedirs(output_path + str(id))

    output = os.path.join(output_path + str(id), filename)
    if src.lower().startswith("http"):
        urlretrieve(link, output, reporthook=reporthook)
    else:
        urlretrieve(urlunparse(parsed), output, reporthook=reporthook)


def parse_home_page(url, html):
    soup = BeautifulSoup(html, "html.parser")
    i = Home()
    global data
    data = {}
    child_id = data_begin_id

    def parse_carousel(pass_id):
        carousel_list = soup.select('div.carousel-inner > div > a')
        for c in carousel_list:
            href = c.get('href')
            if href is None:
                continue
            if "season" not in href:
                continue
            src = ''
            name = ''
            captioin = ''
            # print(href)
            for d in c.findAll('div', class_="carousel_image_crop"):
                # print(d.find('img')['src'])
                src = d.find('img')['src']
                break;
            for d in c.findAll('div', class_="carousel-caption"):
                # print(d.find('h5').getText())
                # print(d.find('p').getText())
                name = d.find('h5').getText()
                captioin = d.find('p').getText()
                break;
            process_image(url, src, pass_id)
            base_url = '/static/' + str(pass_id) + '/'
            file = os.path.basename(src)
            ext = os.path.splitext(file)[0] + '.jpg'
            item = {'id': str(pass_id), 'name': name, 'caption': captioin, 'src': base_url + ext, 'href': href}
            # print(item)
            i.carousel.append(item)
            pass_id +=1
        return pass_id

    def parse_new_recommend(pass_id):
        global data
        new_recommend = soup.select('div.new_recommend > div > div > a')
        for r in new_recommend:
            href = r.get('href')
            if href is None:
                href = ''
            episode = ''
            src = ''
            name = ''
            description = ''
            for d in r.findAll('div', class_="img_hover_effect"):
                episode = d.find('p').getText()
                src = d.find('img')['src']
                break
            for d in r.findAll('div', class_="item_info"):
                name = d.find('p', class_="item_name").getText()
                description = d.find('p', class_="item_description").getText()
                break
            process_image(url, src, pass_id)
            base_url = '/static/' + str(pass_id) + '/'
            file = os.path.basename(src)
            ext = os.path.splitext(file)[0] + '.jpg'
            item = {'id': str(pass_id), 'name': name, 'description': description, 'episode': episode,
                    'src': base_url+ext, 'href': href}
            # print(item)
            i.new_recommend.append(item)
            pass_id +=1
        return pass_id

    def parse_series(pass_id):
        global data
        series_list = soup.select('div.curating_block > div')
        label = ''
        href = ''
        # series = []
        for s in series_list:
            items = []
            for h in s.findAll('h3'):
                label = h.find('a').getText()
                href = h.find('a')['href']
                break

            if "item_lists" in s['class']:
                # print("===")
                for div in s.findAll('div'):
                    info = div.select_one('a > div.item_info')
                    if info is not None:
                        name = info.find('p', class_="item_name").getText()
                        episode = info.find('p', class_="item_episode").getText()
                    else:
                        continue

                    a = div.find('a')
                    if a is not None:
                        href = a['href']

                    img = div.find('img')
                    if img is not None:
                        src = img['src']

                    process_image(url, src, pass_id)
                    base_url = '/static/' + str(pass_id) + '/'
                    file = os.path.basename(src)
                    ext = os.path.splitext(file)[0] + '.jpg'
                    item = {'id': str(pass_id), 'name': name, 'description': '', 'episode': episode,
                            'src': base_url+ext, 'href': href}
                    items.append(item)
                    pass_id +=1
                # print("===")
            else:
                continue

            s = {'label': label, 'href': href, 'items': items}
            i.series.append(s)

        return pass_id
        # print(series)

    b = parse_carousel(child_id)
    c = parse_new_recommend(b)
    parse_series(c)

    data = i


def get_home_page(url):
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    browser = webdriver.Chrome(options=options, executable_path='bin/chromedriver.exe')
    browser.implicitly_wait(30)
    browser.get(url)

    browser.find_element_by_class_name('carousel-caption')
    html = browser.page_source
    parse_home_page(url, html)


def read_urls():
    with open('home_page.txt') as f:
        line = f.readlines()
        line = [x.strip() for x in line]

    for url in line:
        if not url.startswith('#'):
            get_home_page(url)

    on_parse_complate()


if __name__ == "__main__":
    read_urls()
