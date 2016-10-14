# -*- coding: utf-8 -*-

from weibo import APIClient, APIError
import sys
import mid

# weico app key
# https://github.com/wenmingvs/WeiBo/blob/173687ed2a32b3b59a37354caaa662314b3a928d/weiSwift/src/main/java/com/wenming/weiswift/ui/common/login/Constants.java

# API wiki
# https://github.com/michaelliao/sinaweibopy/wiki/OAuth2-HOWTO

APP_KEY = "211160679" # app key
APP_SECRET = "1e6e33db08f9192306c4afa0a61ad56c" # app secret
REDIRECT_URL = "http://oauth.weico.cc" # callback url
SCOPE = "email,direct_messages_read,direct_messages_write,friendships_groups_read,friendships_groups_write,statuses_to_me_read,follow_app_official_microblog,invitation_write"
PACKAGE_NAME = "com.eico.weico"

authurl = "https://open.weibo.cn/oauth2/authorize" + "?" + "client_id=" + APP_KEY + "&response_type=token&redirect_uri=" + REDIRECT_URL + "&key_hash=" + APP_SECRET + "&packagename=" + PACKAGE_NAME + "&display=mobile" + "&scope=" + SCOPE
# https://open.weibo.cn/oauth2/authorize?client_id=211160679&response_type=token&redirect_uri=http://oauth.weico.cc&key_hash=1e6e33db08f9192306c4afa0a61ad56c&packagename=com.eico.weico&display=mobile&scope=email,direct_messages_read,direct_messages_write,friendships_groups_read,friendships_groups_write,statuses_to_me_read,follow_app_official_microblog,invitation_write

client = None

def set_client(access_token, expires_in):
	global client
	client = APIClient(app_key=APP_KEY, app_secret=APP_SECRET, redirect_uri=REDIRECT_URL)
	client.set_access_token(access_token, expires_in)

def get_auth_url():
	return authurl

def user_timeline(uid, count, max_id=None, since_id=None, trim_user=1):
	response = client.statuses.user_timeline.get(uid=uid, count=count, max_id=max_id, since_id=since_id, trim_user=trim_user)
	if max_id is not None:
		result = [item for item in response['statuses'] if item['id'] != max_id]
		return result
	return response['statuses']

def user_timeline_all(uid, response={}):
	max_id = None
	prev_max_id = None
	while True:
		try:
			temp = user_timeline(uid, 199, max_id=max_id)
			if max_id is None:
				max_id = int(temp[0]['id'])
			for item in temp:
				item['mid'] = mid.mid2str(str(item['id']))
				max_id = min(max_id, int(item['id']))
				if item['id'] not in response:
					response[item['id']] = item
			temp = user_timeline(uid, 199, max_id=max_id)
			if len(temp) == 0:
				break
		except Exception:
			return response
	return response
			
def user_timeline_since(uid, since_id, response={}):
	prev_since_id = since_id
	temp_since_id = since_id
	while True:
		print since_id
		try:
			temp = user_timeline(uid, 99, since_id=since_id)
			for item in temp:
				item['mid'] = mid.mid2str(str(item['id']))
				since_id = max(since_id, int(item['id']))
				if item['id'] not in response:
					response[item['id']] = item
			temp = user_timeline(uid, 99, since_id=since_id)
			if len(temp) == 0:
				break
		except Exception:
			return response
	return response

#def weibo(wid):
#	try:
#		response = client.statuses.show.get(id=wid)
#		return response
#	except APIError:
#		return False

def user_info(uid):
	response = client.users.show.get(uid=uid)
	return response

def get_rate_limit():
	response = client.account.rate_limit_status.get()
	return response
