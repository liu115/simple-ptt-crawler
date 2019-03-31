#!/usr/bin/env python
# coding: utf-8

import sys
import os
import requests
import json
import time
import re
from bs4 import BeautifulSoup


# 內頁
def filter_content(content):
    content = content.replace('\n', '')
    match = re.search(r'^(.*?)※\ 發信站:\ 批踢踢實業坊\(ptt\.cc\)', content, re.MULTILINE)
    if match:
        content = match.group(1)
    content = re.sub(r'(<.+?>).*?', '' ,content)
    content = re.sub(r'.*?(</.+?>)', '' ,content)
    
    return content

def parse_page(soup):
    meta_data = soup.find_all(class_='article-metaline')
    author = meta_data[0].find(class_='article-meta-value').text
    title = meta_data[1].find(class_='article-meta-value').text
    date = meta_data[2].find(class_='article-meta-value').text
    
    # 解析內文
    content = soup.find(id='main-content').contents[4:]
    content = ''.join([str(c) for c in content])
    content = filter_content(content)
    
    data = {'author': author, 'title': title, 'date': date, 'content': content }
    return data
    

def crawl_page(page_url):
    res = requests.get(url=page_url, cookies={'over18': '1'})
    soup = BeautifulSoup(res.text, 'html.parser')
    data = parse_page(soup)
    
    return data


# 版面頁
base_url = 'https://www.ptt.cc/bbs/'
def crawl_board(board_name, board_page):
    url = base_url + board_name + '/index' + str(board_page) + '.html'
    res = requests.get(url=url, cookies={'over18': '1'})
    
    soup = BeautifulSoup(res.text, 'html.parser')
    sub_pages = soup.find_all('div', class_='r-ent')
    
    # 用一個 list 把內頁資訊存起來
    sub_page_data_list = []
    
    for sub_page in sub_pages:
        
        # 找推數
        push_info = sub_page.find(class_='nrec').find('span')
        if push_info != None:
            num_push = push_info.text
        else:
            num_push = 0
            
        # 找連結資訊
        link = sub_page.find('a')
        link_url = link['href']
        link_title = link.text
        
        # 找日期
        date = sub_page.find(class_='date').text
                
        sub_page_base_url = 'https://www.ptt.cc'
        sub_page_data = crawl_page(sub_page_base_url + link_url) # 注意，把回傳直接起來
        
        # 補上 link 的資訊
        sub_page_data['link'] = sub_page_base_url + link_url
        sub_page_data['num_push'] = num_push
        
        # 在準備好的 list 上加上這個資訊
        sub_page_data_list.append(sub_page_data)
    
    return sub_page_data_list



# 處理多頁的資訊
def crawl_board_with_range(start, end):
    
    board_data = []
    for page_id in range(start, end):
        print('爬取第', page_id, '頁')
        try:
            page_data = crawl_board('Gossiping', page_id)
            board_data += page_data
        except:
            print('遇到問題，跳過此頁')
            pass
            
    return board_data


# 儲存與讀取
import pickle

# 注意：跑[35000, 35100]有ㄧ100頁，約要一個小時以上。
board_data = crawl_board_with_range(35000, 35010)

# 將爬下來的資料 list 存成 board_data.pkl
with open('board_data.pkl', 'wb') as output:
    pickle.dump(board_data, output)

# 將 board_data.pkl 讀出來到 loaded_board_data 這個變數
with open('board_data.pkl', 'rb') as input:
    loaded_board_data = pickle.load(input)
    print('讀取出來的文章總共有', len(loaded_board_data), '筆')


# 搜尋
def search_word_in_data(data, keyword):
    for page_data in data:
        if keyword in page_data['content']:
            print('在', page_data['title'], '找到', keyword, '關鍵字')            
            print('連結:', page_data['link'])

# 直接把我們儲存的資料讀出來的那份丟進去
search_word_in_data(loaded_board_data, '急診')






