# -*- coding: utf-8 -*-

import requests
from weibo import Client
from pymongo import MongoClient
import datetime
import time
from urllib import quote

__author__ = 'tripleday'

MONGO_HOST = '127.0.0.1'
MONGO_PORT = 27019
MONGO_DB = '500px'
MONGO_USER_COLL = 'photos'
MONGO = MongoClient(MONGO_HOST, MONGO_PORT)

APP_KEY = 'YOUR_APP_KEY'    # 填写申请的APP_KEY
APP_SECRET = 'YOUR_APP_SECRET'    # 填写申请的APP_SECRET
CALLBACK_URL = 'https://api.weibo.com/oauth2/default.html'
USERNAME = 'YOUR_USERNAME'
PASSWORD = 'YOUR_PASSWORD'

client = None

# 获取微博授权，手动操作
def get_client():
    global client
    client = Client(APP_KEY, APP_SECRET, redirect_uri=CALLBACK_URL, username=USERNAME, password=PASSWORD)
    # url = client.get_authorize_url()

    # print url    # 浏览器打开该url，取得code='xxx'类似的code输入

    # headers = {
    #     'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36"
    # }
    # rq = requests.Session()
    # rq.headers = headers
    # r = rq.get(url)

    # code = raw_input('Enter code >')
    # r = client.request_access_token(code)
    # access_token = r.access_token
    # expires_in = r.expires_in
    # print 'access_token:',access_token
    # print 'expires_in:', expires_in
    #
    # client.set_access_token(access_token, expires_in)

# 发微博
def post_img(clock):
    global client
    # text = raw_input('Enter text to post >')
    # utext = unicode(text, "UTF-8")
    # client.statuses.update.post(status=utext)

    p = MONGO[MONGO_DB][MONGO_USER_COLL].find_one({'weibo_sent': False})# have not been sent to weibo
    if not p:
        return
    id = p['_id']
    name = p['name']
    url = p['url']

    # send a weibo with img
    word = str(clock)+' o\'clock 500px photo: '+name.encode('utf-8','ignore')+'. Its URL is: '+url.encode('utf-8','ignore')

    f = open('E:/500px/'+str(id)+'.jpg', 'rb')
    try:
        r = client.post('statuses/upload', status=quote(word), visible=6, pic=f)
    except:
        return
    f.close() # APIClient不会自动关闭文件，需要手动关闭

    # update weibo_sent
    p['weibo_sent'] = True
    MONGO[MONGO_DB][MONGO_USER_COLL].update_one(
        filter={'_id': p['_id']},
        update={'$set': p},
        upsert=False
    )
    print str(clock)+' o\'clock posted!'

if __name__ == '__main__':
     get_client()
     while True:
         now = datetime.datetime.now()
         h = now.hour
         m = now.minute
         if m==0:
             post_img(h)
             time.sleep(3585)

         time.sleep(10)