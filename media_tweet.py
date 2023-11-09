# encoding :utf-8

# ～ 使い方 ～
# ユーザーアクセストークン(CK, CS, AT, ATS)を入力
# コマンドラインから『python media_tweet.py "ツイート本文(省略可)" "1枚目の画像" "2枚目の画像" "3枚目の画像" "4枚目の画像"』
# 引数の順番は厳守。本文または画像のみのツイートも可。投稿テキスト内の改行は{br}で改行される。

import sys, json, __twitter_key, os
from requests_oauthlib import OAuth1Session

CK = __twitter_key.CONSUMER_KEY
CS = __twitter_key.CONSUMER_SECRET
AT = __twitter_key.ACCESS_TOKEN
ATS = __twitter_key.ACCESS_TOKEN_SECRET
twitter = OAuth1Session( CK, CS, AT, ATS )

# TwitterAPIエンドポイントの取得
url_text = 'https://api.twitter.com/2/tweets'
url_media = 'https://upload.twitter.com/1.1/media/upload.json'

# 引数の個数を取得
argc = len( sys.argv )
# ツイート本文・画像を含めた引数の最大値
media_max_val = 6
# 画像ファイルを含んだ引数の始点
start_create_id = 2
# media id格納用
media_ids = []

if argc < 1:
	print( 'sys.argv is none.' )
	sys.exit()

# 本文無しで画像を投稿する用
if os.path.isfile( sys.argv[1] ):
	media_max_val -= 1
	start_create_id -= 1
else:
	# 本文がある場合(改行処理も行う)
	text = sys.argv[1].replace( '{br}', '\n' )

# 画像が5枚以上の時のエラー回避
if argc > media_max_val:
	argc = media_max_val

for i in range( start_create_id, argc ):
	# 画像投稿の準備
	try:  
		media_files = { 'media' : open( sys.argv[i], 'rb' ) }
	except:
		i += 1
		continue
	# Media ID取得
	req_media = twitter.post( url_media, files = media_files )

	# レスポンス確認(v1.1のため200)
	if req_media.status_code != 200:
		print( 'Media Update Failed.' )
		sys.exit()

	# 取得したMedia IDをリストへ詰めていく
	media_ids.append( json.loads( req_media.text )[ 'media_id_string' ] )
	print( 'Media ID: %s' % media_ids )

if os.path.isfile( sys.argv[1] ):
	# 本文が無く、画像のみ場合
	text = {
		'media' : {
			'media_ids' : media_ids
		}
	} 
elif len( media_ids ) == 0:
	# 本文のみの場合
	text = { 'text' : text }
else:
	# 本文・画像共にある場合
	text = {
		'text' : text,
		'media' : {
			'media_ids' : media_ids
		}
	}

# ツイートする
req_media = twitter.post( url_text, json = text )

# ツイート確認(v2のため201)
if req_media.status_code == 201:
	print( 'Tweet Succeed.' )
else:
	print( 'ERROR: %d' % req_media.status_code )
