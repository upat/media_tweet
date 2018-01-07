# encoding :utf-8

# ～ 使い方 ～
# python media_tweet.py "ツイート本文(省略可)" "1枚目の画像" "2枚目の画像" "3枚目の画像" "4枚目の画像"
# 引数の順番は厳守。本文または画像のみのツイートも可。改行は{br}で改行される。

import sys, json, __twitter_key, os
from requests_oauthlib import OAuth1Session

CK = __twitter_key.CONSUMER_KEY
CS = __twitter_key.CONSUMER_SECRET
AT = __twitter_key.ACCESS_TOKEN
ATS = __twitter_key.ACCESS_TOKEN_SECRET
twitter = OAuth1Session(CK, CS, AT, ATS)

# TwitterAPIエンドポイントの取得
url_text = "https://api.twitter.com/1.1/statuses/update.json"
url_media = "https://upload.twitter.com/1.1/media/upload.json"

# 引数の個数を取得
argc = len(sys.argv)
# ツイート本文・画像を含めた引数の最大値
media_max_val = 6
# 画像ファイルを含んだ引数の始点
start_create_id = 2

if argc < 1:
    print('sys.argv is none.')
    sys.exit()

# 本文無しで画像を投稿する用
if os.path.isfile(sys.argv[1]):
    media_max_val -= 1
    start_create_id -= 1
else:
    # 本文がある場合(改行処理も行う)
    text = sys.argv[1].replace('{br}', '\n')

# 画像が5枚以上の時のエラー回避
if argc > media_max_val:
    argc = media_max_val

for i in range(start_create_id, argc):
    # 画像投稿の準備
    try:  
        media_files = {"media" : open(sys.argv[i], 'rb')}
    except:
        i += 1
        continue
    req_media = twitter.post(url_media, files = media_files)

    # レスポンス確認
    if req_media.status_code != 200:
        print('Media Update Failed.')
        sys.exit()

    # Media IDを文字列で取得、2枚目以降の画像がある場合はIDの結合(media_idだとint型?)
    if 'media_id' in locals():
        media_id = media_id + ',' + json.loads(req_media.text)['media_id_string']
        print('Media ID: %s' % media_id)
    else:
        media_id = json.loads(req_media.text)['media_id_string']
        print('Media ID: %s' % media_id)

if os.path.isfile(sys.argv[1]):
    text = {'media_ids' : [media_id]} # 本文が無く、画像のみ場合
elif 'media_id' not in locals():
    text = {'status' : text} # 本文のみの場合
else:
    text = {'status' : text, 'media_ids' : [media_id]} # 本文・画像共にある場合

# ツイートする
req_media = twitter.post(url_text, params = text)

# ツイート確認
if req_media.status_code == 200:
    print('Tweet Succeed.')
else:
    print("ERROR: %d" % req_media.status_code)
