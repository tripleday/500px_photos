# -*- coding: utf-8 -*-

# requirements
import re, json
import requests
from bs4 import BeautifulSoup
import time
import urllib
import cPickle
from pymongo import MongoClient

__author__ = 'tripleday'

MONGO_HOST = '127.0.0.1'
MONGO_PORT = 27019
MONGO_DB = '500px'
MONGO_USER_COLL = 'photos'
MONGO = MongoClient(MONGO_HOST, MONGO_PORT)


# 处理cookie
# cookies = json.load(open('500px_cookie.json'))
headers = {
    'User-Agent': "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:34.0) Gecko/20100101 Firefox/34.0"
}
rq = requests.Session()
rq.headers = headers
# for cookie_item in cookies:
#     rq.cookies[cookie_item['name']] = cookie_item['value']

def download_photos(feature, rounds):
    # check session
    headers = {
    'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36"
    }
    rq = requests.Session()
    rq.headers = headers
    url = "https://500px.com/popular"
    r = rq.get(url, allow_redirects=False)
    status_code = int(r.status_code)
    if status_code != 200:
        print "ERROR!"
        return
    soup = BeautifulSoup(r.content, "html.parser")
    csrf_token = soup.find("meta", attrs={'name': 'csrf-token'})["content"]
    #print csrf_token

    # data = {
    #     'rpp': 50,
    #     'feature':feature,
    #     'image_size[]':1,
    #     'image_size[]':2,
    #     'image_size[]':32,
    #     'image_size[]':31,
    #     'image_size[]':33,
    #     'image_size[]':34,
    #     'image_size[]':35,
    #     'image_size[]':36,
    #     'image_size[]':2048,
    #     'image_size[]':4,
    #     'image_size[]':14,
    #     'sort': '',
    #     'include_states':'true',
    #     'include_licensing':'true',
    #     'formats':'jpeg,lytro',
    #     'only':'',
    #     'page':1,
    #     'rpp':50
    # }


    # r_post = rq.get('https://api.500px.com/v1/photos?rpp=50&feature=popular&image_size%5B%5D=1&image_size%5B%5D=2&image_size%5B%5D=32&image_size%5B%5D=31&image_size%5B%5D=33&image_size%5B%5D=34&image_size%5B%5D=35&image_size%5B%5D=36&image_size%5B%5D=2048&image_size%5B%5D=4&image_size%5B%5D=14&sort=&include_states=true&include_licensing=true&formats=jpeg%2Clytro&only=&page=1&rpp=50', data=data, headers=header)
    # r_post = rq.post(post_url, data=data, headers=header)
    if rounds > 100:
        rounds = 100

    if feature=='popular':
        url = 'https://api.500px.com/v1/photos?rpp=50&feature=popular&image_size%5B%5D=1&image_size%5B%5D=2' \
                    '&image_size%5B%5D=32&image_size%5B%5D=31&image_size%5B%5D=33&image_size%5B%5D=34&image_size%5B%5D=35' \
                    '&image_size%5B%5D=36&image_size%5B%5D=2048&image_size%5B%5D=4&image_size%5B%5D=14&sort=' \
                    '&include_states=true&include_licensing=false&formats=jpeg%2Clytro&only=&rpp=50&page='
        csrf_word = 'X-CSRF-Token'
        csrf = csrf_token
        host = 'api.500px.com'
    elif feature=='editor':
        url = 'https://api.500px.com/v1/photos?rpp=50&feature=editor&image_size%5B%5D=1&image_size%5B%5D=2' \
                    '&image_size%5B%5D=32&image_size%5B%5D=31&image_size%5B%5D=33&image_size%5B%5D=34&image_size%5B%5D=35' \
                    '&image_size%5B%5D=36&image_size%5B%5D=2048&image_size%5B%5D=4&image_size%5B%5D=14&sort=' \
                    '&include_states=true&include_licensing=false&formats=jpeg%2Clytro&only=&rpp=50&page='
        csrf_word = 'X-CSRF-Token'
        csrf = csrf_token
        host = 'api.500px.com'
    elif feature=='stock':
        url = 'https://webapi.500px.com/discovery/stock-photos?rpp=50&feature=stock-photos&image_size%5B%5D=1&image_size%5B%5D=2' \
                    '&image_size%5B%5D=32&image_size%5B%5D=31&image_size%5B%5D=33&image_size%5B%5D=34&image_size%5B%5D=35' \
                    '&image_size%5B%5D=36&image_size%5B%5D=2048&image_size%5B%5D=4&image_size%5B%5D=14&sort=' \
                    '&include_states=true&include_licensing=false&formats=jpeg%2Clytro&only=&rpp=50&page='
        csrf_word = 'AUTHORIZATION'
        csrf = 'PxToken ' + csrf_token
        host = 'webapi.500px.com'
    else:
        return

    header = {
        'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36",
        'Host': host,
        'Origin':"https://500px.com",
        'Referer': "https://api.500px.com",
        csrf_word:csrf
    }

    for round in xrange(rounds):
        r_post = rq.get(url+str(round+1), headers=header)

        # f = open("C:/Users/Wu/Desktop/500px/content.pkl",'wb')
        # cPickle.dump(r_post.json(),f,-1)
        # f.close()

        for p in r_post.json()['photos']:
            id = p['id']
            if not MONGO[MONGO_DB][MONGO_USER_COLL].find_one({'_id': id}):
                name = p['name'].encode('utf-8','ignore')
                for i in p['images']:
                    if i['size']==2048:
                        print i['url']
                        try:
                            urllib.urlretrieve(i['url'],'E:/500px/'+str(id)+'.jpg')
                        except:
                            break
                        item = { '_id':id, 'name':name, 'url':i['url'], 'weibo_sent':False }
                        MONGO[MONGO_DB][MONGO_USER_COLL].insert_one(item)
                        time.sleep(2)
            else:
                print str(id)+' dulplicate!'



if __name__ == '__main__':
    while True:
        download_photos('popular',20)
        download_photos('editor',20)
        download_photos('stock',20)
        print "Sleeping..."
        time.sleep(86400)

