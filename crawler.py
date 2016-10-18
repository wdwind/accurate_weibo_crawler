# -*- coding: utf-8 -*-
import os
import json
import logging
#import locale
import sys
import ssl
import time
#import codecs
import util.logger as logger
from util.weibo_crawler import WeiboCrawler
from util.screenshots_crawler import ScreenshotsCrawler
from util.weibo_writer import export_all
from util.weibo_util import set_client, login_private

def init_config():
	config_file = "config.json"
	# If config file exists, load variables from json
	config = {}
	if os.path.isfile(config_file):
		with open(config_file) as data:
			config.update(json.load(data))
	return config

def main():
	# log settings
	# log format
	#logging.basicConfig(level=logging.DEBUG, format='%(asctime)s [%(module)10s] [%(levelname)5s] %(message)s')
	
	#sys.stdout = codecs.getwriter('utf-8')(sys.stdout)
	#sys.stdout = codecs.getwriter(locale.getpreferredencoding())(sys.stdout)
	#sys.stderr = codecs.getwriter('utf8')(sys.stderr)

	ssl._create_default_https_context = ssl._create_unverified_context

	config = init_config()
	if not config:
		return

	logger.log('[x] Weibo crawler v0.2', 'green')
	logger.log('[x] Configuration initialized')

	set_client(config['access_token'], config['expires_in'])
	j1 = login_private(config['access_token'])
	if j1 is None:
		logger.log('[x] User login fails.', 'red')
		return
	cookie = j1['cookie']['cookie']['.weibo.com']
	config['cookie'] = cookie[4:cookie.index(';')]
	run(config)

def run(config):
	config['mode'] = config['mode'].lower()
	if config['mode'] == 'normal':
		crawler = WeiboCrawler(config)
		crawler.update()
		ss = ScreenshotsCrawler(config)
		ss.retrive()
	elif config['mode'] == 'weibo':
		crawler = WeiboCrawler(config)
		crawler.update()
	elif config['mode'] == 'screenshot':
		ss = ScreenshotsCrawler(config)
		ss.retrive()
	elif config['mode'] == 'loop':
		while True:
			logger.log('[x] ' + '-'*25)
			crawler = WeiboCrawler(config)
			crawler.update()
			ss = ScreenshotsCrawler(config)
			ss.retrive()
			time.sleep(300)
	elif config['mode'] == 'export':
		export_all(config)
	else:
		logger.log('[x] Unknown mode', 'red')

if __name__ == '__main__':
	main()
