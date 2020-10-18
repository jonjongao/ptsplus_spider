# coding=gbk
from bs4 import BeautifulSoup
import codecs
import os
import json

data_begin_id = 5000
read_path = 'raw/'
json_output_path = 'json/result.json'


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


with os.scandir(read_path) as entries:
    data = []
    for e in entries:
        if e.name.endswith('.html'):
            file = codecs.open(e, "r", "utf-8")
            html = file.read()
            soup = BeautifulSoup(html, "html.parser")

            i = Season()

            h1 = soup.find('h1', class_='series_name')
            if h1 is None:
                print('pass file:' + e.name)
                continue

            i.parent = ''
            i.id = data_begin_id + len(data)

            baseUrl = '/static/' + str(i.id) + '/'

            if h1: i.title = h1.getText()

            description = soup.find('div', class_='series_description')
            if description:
                i.desc = description.getText()
                i.caption = 'Equal'
            # i.caption = i.desc = soup.find('div', class_='series_description').getText()
            for a in soup.find_all('div', class_='page_cover_image'):
                src = a.img['src']
                file = os.path.basename(src)
                i.imgSrc = baseUrl + file
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
            for e in episode_list:
                # print(e.img['src'])
                # print(e.p.getText())
                d = {'name': e.p.getText(), 'src': baseUrl+os.path.basename(e.img['src']), 'url': 'javascript:void(0)',
                     'id': 'ep' + str(len(episode_list) - len(i.item))}
                i.item.append(d)

            data.append(i.__dict__)

    print("done")

    d = json.dumps(data, indent=4, ensure_ascii=False)
    with open(json_output_path, 'w', encoding='utf-8') as f:
        f.write(d)

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
