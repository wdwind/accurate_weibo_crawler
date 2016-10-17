# -*- coding: utf-8 -*-

from weibo import APIClient, APIError
import sys
import mid
import requests
import json
import time

# weico app key
# https://github.com/wenmingvs/WeiBo/blob/173687ed2a32b3b59a37354caaa662314b3a928d/weiSwift/src/main/java/com/wenming/weiswift/ui/common/login/Constants.java

# API wiki
# https://github.com/michaelliao/sinaweibopy/wiki/OAuth2-HOWTO

APP_KEY = "211160679" # app key
APP_SECRET = "1e6e33db08f9192306c4afa0a61ad56c" # app secret
REDIRECT_URL = "http://oauth.weico.cc" # callback url
SCOPE = "email,direct_messages_read,direct_messages_write,friendships_groups_read,friendships_groups_write,statuses_to_me_read,follow_app_official_microblog,invitation_write"
PACKAGE_NAME = "com.eico.weico"
CLIENT_NAME = "weicoandroid"

authurl = "https://open.weibo.cn/oauth2/authorize" + "?" + "client_id=" + APP_KEY + "&response_type=token&redirect_uri=" + REDIRECT_URL + "&key_hash=" + APP_SECRET + "&packagename=" + PACKAGE_NAME + "&display=mobile" + "&scope=" + SCOPE
# https://open.weibo.cn/oauth2/authorize?client_id=211160679&response_type=token&redirect_uri=http://oauth.weico.cc&key_hash=1e6e33db08f9192306c4afa0a61ad56c&packagename=com.eico.weico&display=mobile&scope=email,direct_messages_read,direct_messages_write,friendships_groups_read,friendships_groups_write,statuses_to_me_read,follow_app_official_microblog,invitation_write

client = None

def set_client(access_token, expires_in):
	global client
	client = APIClient(app_key=APP_KEY, app_secret=APP_SECRET, redirect_uri=REDIRECT_URL)
	client.set_access_token(access_token, expires_in)

def get_auth_url():
	return authurl

def user_timeline_public(uid, count, max_id=0, since_id=0, trim_user=1):
	response = client.statuses.user_timeline.get(uid=uid, count=count, max_id=max_id, since_id=since_id, trim_user=trim_user)
	return response_filter(response, max_id, since_id)

# http://api.weibo.cn/2/statuses/user_timeline?access_token=%s&since_id=%d&max_id=%d&count=%d&uid=%s&gsid=%s&source=%s&c=%s&trim_user=%d
def user_timeline_private(uid, count, max_id=0, since_id=0, trim_user=1):
	url = 'http://api.weibo.cn/2/statuses/user_timeline?access_token=%s&since_id=%d&max_id=%d&count=%d&uid=%s&gsid=%s&source=%s&c=%s&trim_user=%d'
	req = requests.get(url % (client.access_token, since_id, max_id, count, uid, gsid, APP_KEY, CLIENT_NAME, trim_user), timeout=30)
	response = json.loads(req.text)
	return response_filter(response, max_id, since_id, contains_like=True)

def response_filter(response, max_id, since_id, contains_like=False):
	if 'errno' in response:
		return None
	result = response['statuses']
	for item in result:
		item['uid'] = item['user']['id']
	if contains_like:
		result = [item for item in result if ('like_status' not in item)]
	if since_id != 0:
		result = [item for item in result if (item['id'] > since_id)]
	if max_id != 0:
		result = [item for item in result if (item['id'] < max_id)]
	return result

#def user_timeline_all_public(uid, num_weibos, response={}):
#	max_id = 0
#	while True:
#		try:
#			if len(response) == num_weibos:
#				return response
#			temp = user_timeline_public(uid, 30, max_id=max_id)
#			if temp is None:
#				continue
#			if len(temp) == 0:
#				temp = user_timeline_private(uid, 30, max_id=max_id)
#				if len(temp) == 0:
#					return response
#			for item in temp:
#				if item['id'] in response:
#					continue
#				item['mid'] = mid.mid2str(str(item['id']))
#				response[item['id']] = item

#			time.sleep(4)
#		except Exception:
#			return response
#	return response

def user_timeline_all(uid, num_weibos, response={}, user_timeline_func=user_timeline_private, count=30):
	max_id = 0
	while True:
		try:
			if len(response) == num_weibos:
				return response
			temp = user_timeline_func(uid, count, max_id=max_id)
			if temp is None:
				continue
			if len(temp) == 0:
				temp = user_timeline_func(uid, count, max_id=max_id)
				if len(temp) == 0:
					return response
			for item in temp:
				if item['id'] in response:
					continue
				item['mid'] = mid.mid2str(str(item['id']))
				response[item['id']] = item
			max_id = int(temp[-1]['id'])
			time.sleep(1)
		except Exception, e:
			# print repr(e)
			return response
	return response
			
def user_timeline_all_since(uid, since_id, num_weibos, response={}, user_timeline_func=user_timeline_private, count=30):
	while True:
		try:
			if len(response) == num_weibos:
				return response
			temp = user_timeline_func(uid, count, since_id=since_id)
			if temp is None:
				continue
			if len(temp) == 0:
				temp = user_timeline_func(uid, count, since_id=since_id)
				if len(temp) == 0:
					break
			for item in temp:
				item['mid'] = mid.mid2str(str(item['id']))
				#since_id = max(since_id, int(item['id']))
				if item['id'] not in response:
					response[item['id']] = item
			since_id = max([item['id'] for item in temp])
			time.sleep(1)
		except APIError, e:
			# print repr(e)
			return response
	return response

def weibo(wid):
	try:
		response = client.statuses.show.get(id=wid)
		return response
	except APIError, e:
		# print str(e)
		return None

def weibo_exists_m(mid, uid, cookie):
	url = 'http://m.weibo.cn/1/%s' % (mid)
	req = None
	for i in xrange(3):
		try:
			req = requests.get(url, cookies={'SUB': cookie}, timeout=30)
			break
		except Exception, e:
			# print str(e)
			# print 'Retry'
			pass
	if req is None: return False
	nofound = req.text.find('nofound-desc')
	contain_uid = req.text.find(str(uid))
	if nofound != -1 and contain_uid == -1:
		return False
	else:
		return True

def weibo_exists(mid):
	url = 'http://weibo.cn/comment/%s' % (mid)
	req = None
	for i in xrange(5):
		try:
			req = requests.get(url, timeout=30)
			break
		except Exception, e:
			# print str(e)
			# print 'Retry'
			pass
	if req is None: return False
	if 'target weibo does not exist!' in req.text:
		return False
	else:
		return True

def user_info(uid):
	response = client.users.show.get(uid=uid)
	return response

def get_rate_limit():
	response = client.account.rate_limit_status.get()
	return response

gsid = None

def login_private(token):
	url = 'http://api.weibo.cn/2/account/login'
	data = {'access_token' : token, 'source': APP_KEY, 'getcookie' : 1}
	req = requests.post(url, data=data, timeout=30)
	response = json.loads(req.text)
	if 'gsid' not in response:
		return None
	global gsid
	gsid = response['gsid']
	return response