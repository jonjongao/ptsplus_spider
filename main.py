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

data_begin_id = 5000
read_path = 'raw/'
json_output_path = 'json/result2.json'
output_path = 'json/'


class Home:
    carousel = []
    new_recommend = []
    series = []

    def __init__(self):
        self.carousel = []
        self.new_recommend = []
        self.series = []


class Season:
    parent = ''
    id = ''
    title = ''
    caption = ''
    imgSrc = ''
    date = ''
    epNum = ''
    desc = ''
    direct = ''
    actor = ''
    category = []
    url = ''
    active = []
    item = []


data = []
digging_max_depth = 1
ignore_file = ['app-store.png', 'google-play.png', 'pts_logo_l.png']


def compress_image():
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
                    rgb_img.save(p, optimize=True, quality=30)
                    a_size = os.path.getsize(p)
                    os.remove(e.path)
                    # print("size after compress:" + str(a_size))
                else:
                    img.save(e.path, optimize=True, quality=30)
                    a_size = os.path.getsize(e.path)
                    # print("size after compress:" + str(a_size))


def reporthook(a, b, c):
    """
    显示下载进度
    :param a: 已经下载的数据块
    :param b: 数据块的大小
    :param c: 远程文件大小
    :return: None
    """
    print("\rdownloading: %5.1f%%" % (a * b * 100.0 / c), end="")


def on_parse_complate():
    print("is done")
    d = json.dumps(data, indent=4, ensure_ascii=False)
    # print(d)
    with open(json_output_path, 'w', encoding='utf-8') as f:
        f.write(d)
    compress_image()


def parse_index(url, html):
    soup = BeautifulSoup(html, "html.parser")


def parse_html(url, parent: Season, html):
    soup = BeautifulSoup(html, "html.parser")
    i = Season()
    h1 = soup.find('h1', class_='series_name')
    if h1 is None:
        print('pass url:' + url)
        return

    if h1:
        title = h1.getText()
    else:
        title = ''

    if parent is None or parent == '':
        i.parent = ''
        i.id = data_begin_id + len(data)
    else:
        i.parent = str(parent.id)
        for item_child in parent.item:
            if item_child['name'] == title:
                i.id = item_child['id']
                break

        if i.id is None or i.id == '':
            i.id = ''

    i.title = title

    base_url = '/static/' + str(i.id) + '/'

    description = soup.find('div', class_='series_description')
    if description:
        i.desc = description.getText()
        i.caption = '__equal__'
    # i.caption = i.desc = soup.find('div', class_='series_description').getText()
    for a in soup.find_all('div', class_='page_cover_image'):
        src = a.img['src']
        file = os.path.basename(src)
        ext = os.path.splitext(file)[0] + '.jpg'
        i.imgSrc = base_url + ext
        break

    date = soup.find('div', class_='publish_date')
    if date: i.date = date.getText()

    num = soup.find('div', class_='episode_num')
    if num: i.epNum = num.getText()

    direct = soup.find('div', class_='series_direct')
    if direct: i.direct = direct.getText()

    actor = soup.find('div', class_='series_actor')
    if actor: i.actor = actor.getText()

    i.category = []
    for c in soup.select('ul.series_category > li > a'):
        i.category.append(c.getText().strip())

    i.url = '/season/:id'
    i.active = []
    for a in soup.select('div.series_episode_btn_bar > ul > li > a'):
        i.active.append(a.getText().strip())

    i.item = []
    episode_list = soup.select('app-season-episode-side-list > div > a')
    child_id = i.id
    for e in episode_list:
        # print(e.img['src'])
        # print(e.p.getText())
        # d = {'name': e.p.getText(), 'src': base_url + os.path.basename(e.img['src']), 'url': 'javascript:void(0)',
        #      'id': 'ep' + str(len(episode_list) - len(i.item))}
        child_id += 1
        file = os.path.basename(e.img['src'])
        ext = os.path.splitext(file)[0] + '.jpg'
        d = {'name': e.p.getText(), 'src': base_url + ext, 'url': 'javascript:void(0)',
             'id': child_id}
        i.item.append(d)
        depth_1_url = e['href']
        parsed_uri = urlparse(url)
        domain = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
        # print(domain + depth_1_url)
        get_url(domain[:-1] + depth_1_url, i, 1)

    parsed = list(urlparse(url))
    for image in soup.findAll("img"):
        # print("Image: %(src)s" % image)
        link = urllib.parse.quote(image["src"], safe=':/')
        filename = os.path.basename(image["src"])
        if filename in ignore_file:
            print("ignore file:" + filename)
            continue
        parsed[2] = link

        if not os.path.exists(output_path + str(i.id)):
            os.makedirs(output_path + str(i.id))

        output = os.path.join(output_path + str(i.id), filename)
        if image["src"].lower().startswith("http"):
            urlretrieve(link, output, reporthook=reporthook)
        else:
            urlretrieve(urlunparse(parsed), output, reporthook=reporthook)

    data.append(i.__dict__)


def get_url(url, parent: Season = None, depth=0):
    print("start digging " + url + " in depth " + str(depth))
    if depth > digging_max_depth:
        print("digging reach limit")
        return
    browser = webdriver.Chrome('bin/chromedriver.exe')
    browser.implicitly_wait(30)
    browser.get(url)

    browser.find_element_by_class_name('series_name')
    html = browser.page_source
    parse_html(url, parent, html)


def parse_home_page(url, html):
    soup = BeautifulSoup(html, "html.parser")
    i = Home()

    def parse_carousel():
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
            item = {'name': name, 'caption': captioin, 'src': src, 'href': href}
            # print(item)
            i.carousel.append(item)

    def parse_new_recommend():
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
            item = {'name': name, 'description': description, 'episode': episode, 'src': src, 'href': href}
            # print(item)
            i.new_recommend.append(item)

    def parse_series():
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

                    item = {'name': name, 'description': '', 'episode': episode, 'src': src, 'href': href}
                    items.append(item)
                # print("===")
            else:
                continue

            s = {'label': label, 'href': href, 'items': items}
            i.series.append(s)
        # print(series)


        # with open(json_output_path, 'w', encoding='utf-8') as f:
        #     f.write(d)
        # src = r.find('img')['src']
        # name = r.find('p', class_="item_name").getText()
        # episode = r.find('p', class_="item_episode").getText()
        # item = {'name': name, 'description': '', 'episode': episode, 'src': src, 'href': href}
        # series.append(item)

    parse_carousel()
    parse_new_recommend()
    parse_series()

    d = json.dumps(i.__dict__, indent=4, ensure_ascii=False)
    # print(d)
    with open('json/home.json', 'w', encoding='utf-8') as f:
        f.write(d)

def get_home_page(url):
    browser = webdriver.Chrome('bin/chromedriver.exe')
    browser.implicitly_wait(30)
    browser.get(url)

    browser.find_element_by_class_name('carousel-caption')
    html = browser.page_source
    parse_home_page(url, html)


def read_urls():
    def read_home_page():
        with open('home_page.txt') as f:
            line = f.readlines()
            line = [x.strip() for x in line]

        for url in line:
            if not url.startswith('#'):
                get_home_page(url)

    def read_season_page():
        with open('season.txt') as f:
            line = f.readlines()
            line = [x.strip() for x in line]

        for url in line:
            if not url.startswith('#'):
                get_url(url)

        on_parse_complate()

    # read_home_page()
    # read_season_page()

    with os.scandir('raw3/') as entries:
        for e in entries:
            if e.name.endswith('.html'):
                file = codecs.open(e, "r", "utf-8")
                html = file.read()
                parse_home_page('raw3/index.html', html)


if __name__ == "__main__":
    read_urls()

# with os.scandir(read_path) as entries:
#     data = []
#     for e in entries:
#         if e.name.endswith('.html'):
#             file = codecs.open(e, "r", "utf-8")
#             html = file.read()
#             soup = BeautifulSoup(html, "html.parser")
#
#             i = Season()
#
#             h1 = soup.find('h1', class_='series_name')
#             if h1 is None:
#                 print('pass file:' + e.name)
#                 continue
#
#             i.parent = ''
#             i.id = data_begin_id + len(data)
#
#             baseUrl = '/static/' + str(i.id) + '/'
#
#             if h1: i.title = h1.getText()
#
#             description = soup.find('div', class_='series_description')
#             if description:
#                 i.desc = description.getText()
#                 i.caption = 'Equal'
#             # i.caption = i.desc = soup.find('div', class_='series_description').getText()
#             for a in soup.find_all('div', class_='page_cover_image'):
#                 src = a.img['src']
#                 file = os.path.basename(src)
#                 i.imgSrc = baseUrl + file
#                 break
#
#             date = soup.find('div', class_='publish_date')
#             if date: i.date = date.getText()
#
#             num = soup.find('div', class_='episode_num')
#             if num: i.epNum = num.getText()
#
#             direct = soup.find('div', class_='series_direct')
#             if direct: i.direct = direct.getText()
#
#             actor = soup.find('div', class_='series_actor')
#             if actor: i.actor = actor.getText()
#
#             i.category = []
#             for c in soup.select('ul.series_category > li > a'):
#                 i.category.append(c.getText().strip())
#
#             i.url = '/season/:id'
#             i.active = []
#             for a in soup.select('div.series_episode_btn_bar > ul > li > a'):
#                 i.active.append(a.getText().strip())
#
#             i.item = []
#             episode_list = soup.select('app-season-episode-side-list > div > a')
#             for e in episode_list:
#                 # print(e.img['src'])
#                 # print(e.p.getText())
#                 d = {'name': e.p.getText(), 'src': baseUrl+os.path.basename(e.img['src']), 'url': 'javascript:void(0)',
#                      'id': 'ep' + str(len(episode_list) - len(i.item))}
#                 i.item.append(d)
#
#             data.append(i.__dict__)
#
#     print("done")
#
#     d = json.dumps(data, indent=4, ensure_ascii=False)
#     with open(json_output_path, 'w', encoding='utf-8') as f:
#         f.write(d)

# attrs = vars(i)
# print('\n'.join("%s: %s" % item for item in attrs.items()))
#
# # print(json.dumps(i.__dict__, ensure_ascii=False))
# j = json.dumps(i.__dict__, indent=4, ensure_ascii=False)
# with open('json/1.json', 'w', encoding='utf-8') as f:
#     f.write(j)

# b = soup.select('div.page_cover_image > img[src]')
# for t in b:
#     print(t['src'])
