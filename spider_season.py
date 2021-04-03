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


class Season:
    raw_url = ''
    parent = ''
    id = ''
    name = ''
    caption = ''
    src = ''
    date = ''
    episode = ''
    description = ''
    direct = ''
    actor = ''
    category = []
    active = []


data_begin_id = 7302
output_path = 'json4/'
data = []
dumped_data = []
digging_max_depth = 1
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
                    rgb_img.save(p, optimize=True, quality=20)
                    a_size = os.path.getsize(p)
                    os.remove(e.path)
                    # print("size after compress:" + str(a_size))
                else:
                    ext = os.path.splitext(e.name)[0] + '.jpg'
                    p = entry.path + "/" + ext
                    img.save(p, optimize=True, quality=20)
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
    dumped_data = []
    for d in data:
        d.id = str(d.id)
        dumped_data.append(d.__dict__)
    out = json.dumps(dumped_data, indent=4, ensure_ascii=False)
    # print(out)
    with open(output_path+'result.json', 'w', encoding='utf-8') as f:
        f.write(out)
    # compress_image()


def already_in_data(url):
    for i in data:
        if i.raw_url == url:
            print("!! " + i.name + " is already in data")
            return i
    return None


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


def parse_html(driver, url, id_override, parent: Season, html):
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

    i.raw_url = url

    has_data = already_in_data(url)
    if has_data is not None:
        return

    if parent is None or parent == '':
        i.parent = ''
        i.id = data_begin_id + len(data)
    else:
        i.parent = str(parent.id)
        i.id = str(id_override)
        # for item_active in parent.active:
        #     for item_child in item_active['items']:
        #         if item_child['name'] == title:
        #             print("bind child["+str(item_child['id'])+"] to "+str(parent.id))
        #             i.id = str(item_child['id'])
        #             break

        if i.id is None or i.id == '':
            i.id = ''

    i.name = title

    base_url = '/static/' + str(i.id) + '/'

    description = soup.find('div', class_='series_description')
    if description:
        i.description = description.getText()
        i.caption = '__equal__'
    # i.caption = i.desc = soup.find('div', class_='series_description').getText()
    for a in soup.find_all('div', class_='page_cover_image'):
        src = a.img['src']
        file = os.path.basename(src)
        ext = os.path.splitext(file)[0] + '.jpg'
        i.src = base_url + ext
        process_image(url, src, i.id)
        break

    date = soup.find('div', class_='publish_date')
    if date: i.date = date.getText()

    num = soup.find('div', class_='episode_num')
    if num: i.episode = num.getText()

    direct = soup.find('div', class_='series_direct')
    if direct: i.direct = direct.getText()

    actor = soup.find('div', class_='series_actor')
    if actor: i.actor = actor.getText()

    i.category = []
    for c in soup.select('ul.series_category > li > a'):
        i.category.append(c.getText().strip())

    # i.url = '/season/:id'



    for a in soup.select('div.series_episode_btn_bar > ul > li > a'):
        label = a.getText().strip()
        item = []

        episode_buttons = driver.find_elements_by_xpath("//a[@href='javascript:void(0);']")
        '''
        在子頁面因找不到app-season-episode-side-list
        引此item就自動不會被處理
        '''

        if parent is None or parent == '':
            if len(episode_buttons) > 1:
                i.active = []
                child_id = i.id
                for index in range(2):
                    item = []
                    print("processing episode menu:" + str(index))
                    sub = episode_buttons[index]
                    sub.click()
                    time.sleep(1)

                    # driver.find_element_by_class_name('series_name')
                    html = driver.page_source
                    soup = BeautifulSoup(html, "html.parser")
                    episode_list = soup.select('app-season-episode-side-list > div > a')
                    active_label = soup.select_one('li.active > a')
                    for e in episode_list:
                        label = active_label.getText().strip()
                        child_id += 1
                        file = os.path.basename(e.img['src'])
                        ext = os.path.splitext(file)[0] + '.jpg'
                        d = {'name': e.p.getText(), 'src': base_url + ext, 'url': 'javascript:void(0)',
                             'id': child_id}
                        process_image(url, e.img['src'], i.id)
                        item.append(d)
                        depth_1_url = e['href']
                        parsed_uri = urlparse(url)
                        domain = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
                        get_url(domain[:-1] + depth_1_url, child_id, i, 1)

                    act_obj = {'label': label, 'items': item}
                    i.active.append(act_obj)
            else:
                i.active = []
                episode_list = soup.select('app-season-episode-side-list > div > a')
                child_id = i.id
                for e in episode_list:
                    child_id += 1
                    file = os.path.basename(e.img['src'])
                    ext = os.path.splitext(file)[0] + '.jpg'
                    d = {'name': e.p.getText(), 'src': base_url + ext, 'url': 'javascript:void(0)',
                         'id': child_id}
                    process_image(url, e.img['src'], i.id)
                    item.append(d)
                    depth_1_url = e['href']
                    parsed_uri = urlparse(url)
                    domain = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
                    # print(domain + depth_1_url)

                    get_url(domain[:-1] + depth_1_url, child_id, i, 1)

                    act_obj = {'label': label, 'items': item}
                    i.active.append(act_obj)



    data.append(i)
    progress = int((len(data) / url_length) * 100)
    # print("Progress:" + str(progress) + "%")


def get_url(url, id_override = 0, parent: Season = None, depth = 0):
    end = url.rsplit('/', 1)[-1]
    if depth == 0:
        print("-- start digging " + end + " in depth " + str(depth))
    elif depth == 1:
        global url_length
        url_length += 1
        print(" |- start digging " + end + " in depth " + str(depth))
    if depth > digging_max_depth:
        print("digging reach limit")
        return

    response = urllib.request.urlopen('http://google.com')
    if response.code == 404:
        print("missing url:"+url)
        return
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    browser = webdriver.Chrome(options=options, executable_path='bin/chromedriver.exe')
    # browser = webdriver.Chrome('bin/chromedriver.exe')

    browser.implicitly_wait(30)
    browser.get(url)

    browser.find_element_by_class_name('series_name')
    html = browser.page_source
    parse_html(browser, url, id_override, parent, html)


def read_urls():
    global url_length
    with open('season.txt', "r", encoding="utf-8") as f:
        line = f.readlines()
        line = [x.strip() for x in line]
        for l in line:
            if not l.startswith("#"):
                url_length += 1
        print("Url length:" + str(url_length))

    for url in line:
        if not url.startswith('#'):
            get_url(url)

    on_parse_complate()


if __name__ == "__main__":
    read_urls()
