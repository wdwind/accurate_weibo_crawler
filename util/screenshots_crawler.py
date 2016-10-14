import os
#import subprocess
from subprocess import list2cmdline
import logger
import db_util
import json
import envoy

def path_to_unix(path):
	paths = path.split(os.sep)
	return '/'.join(paths)

class ScreenshotsCrawler:
	def __init__(self, config):
		self.conf = config
		self.wids = None
		#self.cookies = dict(SUB=self.conf['SUB'])
		#self.validity_check()

	# use `envoy` instead of `subprocess` because envoy support `timeout`
	# similar packages:
	#   sh plumbum sarge EasyProcess
	def capture_screenshot(self, url, destination, cookie='', timeout=30000):
		logger.log("[#] Capture screenshot %s, and put it in %s" % (url, destination))
		#subprocess.call([self.phantomjs_folder + 'phantomjs.exe', self.phantomjs_folder + 'rasterize6_cookies.js', url, destination, str(timeout), cookie])
		cmd = list2cmdline([path_to_unix(self.phantomjs), \
			'./util/rasterize6_cookies.js', \
			url, path_to_unix(destination), str(timeout), cookie])
		r = envoy.run(str(cmd), timeout=60+timeout/1000)

	def validity_check(self, entry):
		out_folder = entry['screenshots_path']
		if out_folder[-1] != '/':
			out_folder += '/'
		temp_out_folder=entry['temp_screenshots_path']
		if temp_out_folder[-1] != '/':
			temp_out_folder += '/'
		phantomjs = self.conf['phantomjs']
		if not os.path.exists(out_folder):
			os.mkdir(entry['screenshots_path'])
		if not os.path.exists(temp_out_folder):
			os.mkdir(entry['temp_screenshots_path'])
		if not os.path.isfile(phantomjs):
			logger.log('[x] You need to download PhantomJs!', 'red')
			return False
		self.out_folder = out_folder
		self.temp_out_folder = temp_out_folder
		self.phantomjs = phantomjs

	def retrive(self):
		for entry in self.conf['tasks']:
			if self.validity_check(entry) is False:
				continue
			logger.log('[x] Retrive user %s\'s screenshots.' % (entry['uid']))
			self.retrive_weibo(entry)
			self.retrive_hot_comments(entry)

	def retrive_weibo(self, entry):
		uid = entry['uid']
		wids = self.get_wids(uid)
		captured_wids = self.get_captured_wids()
		wids_retrive = []
		for wid in wids:
			if wid not in captured_wids:
				wids_retrive.append(wid)

		for wid in wids_retrive:
			url = 'http://m.weibo.cn/' + uid + '/' + wid
			destination = self.temp_out_folder + wid + '.png'
			self.capture_screenshot(url, destination, timeout=self.conf['timeout'])

	def retrive_hot_comments(self, entry):
		if entry['screenshots_hot_comments'] is False or self.conf['cookie'] is None or self.conf['cookie'] == '':
			return
		uid = entry['uid']
		wids = self.get_wids(uid)
		captured_wids = self.get_captured_wids(True)
		wids_retrive = []
		for wid in wids:
			if wid not in captured_wids:
				wids_retrive.append(wid)

		for wid in wids_retrive:
			url = 'http://m.weibo.cn/single/rcList?id=' + wid + '&type=comment&hot=1'
			destination = self.temp_out_folder + wid + '_hot_comments.png'
			self.capture_screenshot(url, destination, self.conf['cookie'], timeout=self.conf['timeout'])

	def get_wids(self, uid):
		sql = 'SELECT mid FROM status WHERE deleted=-1 AND uid=? ORDER BY id desc'
		wids = db_util.execute(self.conf['db'], sql, [uid])
		wids = [json.loads(item[0]) for item in wids]
		return wids

	def get_captured_wids(self, hot=False):
		files = os.listdir(self.out_folder) + os.listdir(self.temp_out_folder)
		files_set = []
		for filename in files:
			if hot:
				if len(filename) > 17 and 'hot_comments' in filename:
					files_set.append(filename[:-17])
			else:
				if len(filename) > 4 and 'hot' not in filename:
					files_set.append(filename[:-4])
		files_set = set(files_set)
		return files_set