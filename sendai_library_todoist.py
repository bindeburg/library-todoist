import logging
import re
import mechanicalsoup as ms
import requests
import datetime
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import todoist
import argparse
import configparser
import os

# メールアドレスとパスワードの指定
USER = "0009808049"
PASS = "Bruckner5th"

# ログイン情報
login_info = {
    "txt_usercd": USER,
    "txt_password": PASS,
    "submit_btn_login": "ログイン",
}

# セッション開始
s = requests.Session()
r = s.get('https://lib-opac.smt.city.sendai.jp/winj/opac/login.do?lang=ja&dispatch=/opac/mylibrary.do')
soup = BeautifulSoup(r.text)
#auth_token = soup.find(attrs={'name': 'authenticity_token'}).get('value')
# print(auth_token)
#payload['authenticity_token'] = auth_token


# ログイン
res = s.post(
    'https://lib-opac.smt.city.sendai.jp/winj/opac/login.do?lang=ja&dispatch=/opac/mylibrary.do', data=login_info)
res.raise_for_status()
#print(res.text)

#借りている本の情報を取得
r = s.get('https://lib-opac.smt.city.sendai.jp/winj/opac/lend-list.do')
soup = BeautifulSoup(r.text)
raw_booklist = soup.find_all('span', class_='title')
#タイトルのみを抽出
booklist = [x.text.replace('【図書】', '').replace('\n', '') for x in raw_booklist]
print(booklist)

#返却予定日を抽出
raw_duelist = soup.find_all('div', class_='column info')
#返却期限日のみを抽出
cut_duelist = [x.text.replace('\n', ' ') for x in raw_duelist]
duelist_0 = []
duelist = []
for x in cut_duelist:
    x = re.findall('返却期限日:\d+/\d+/\d+', x)
    duelist_0 += x
for x in duelist_0:
    x = re.findall('\d+/\d+/\d+', x)
    duelist += x
print(duelist)

book_dict = dict(zip(booklist, duelist))
print(book_dict)

#TodoistのAPI読み込み
api = todoist.TodoistAPI('9ec420d4a956e8ebd25af7d7b58fd3e58b86b40d')
api.sync()

#Todoistのタスクと照合

#Todoistにタスク追加
for x, y in book_dict.items():
    y = y.replace('/', '-')
    item = api.items.add(x, project_id=2210710301, due={
                         "date": y}, labels=[2156943584])
    api.commit()
