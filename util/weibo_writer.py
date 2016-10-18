import sqlite3
import csv
import codecs
import db_util
import json
import time
import logger

class ChineseWriter:
    """
    A CSV writer which will write (Chinese) rows to CSV file "f", 
    which is encoded in utf-8.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        # Redirect output to a queue
        f.write(codecs.BOM_UTF8)
        self.writer = csv.writer(f, dialect=dialect, **kwds)

    def writerow(self, row):
        self.writer.writerow([unicode(s).encode("utf-8") for s in row])

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)

def table_to_csv(db, sql, out='weibos.csv', headers=None):
	rows = db_util.execute(db, sql)
	rows = pre_process(rows)
	writer = ChineseWriter(open(out, "wb"))
	if headers is not None:
		writer.writerow(headers)
	writer.writerows(rows)

def pre_process(rows):
	de_jsnfied_rows = []
	pic = headers.index('pic_infos')
	retweet = headers.index('retweeted_status')
	for row in rows:
		temp = [json.loads(item) if isinstance(item, unicode) else item for item in row]
		temp = [item.replace('\n', '\\n') if isinstance(item, unicode) else item for item in temp]
		if temp[pic] != '':
			pic_infos = temp[pic]
			pics = [pic_infos[ind]['largest']['url'] for ind in pic_infos]
			pics = ','.join(pics)
			temp[pic] = pics
		if temp[retweet] != '':
			retweeted_text = temp[retweet]['text']
			temp[retweet] = retweeted_text
		de_jsnfied_rows.append(temp)
	return de_jsnfied_rows

#def byteify(input):
#    if isinstance(input, dict):
#        return {byteify(key): byteify(value)
#                for key, value in input.iteritems()}
#    elif isinstance(input, list):
#        return [byteify(element) for element in input]
#    elif isinstance(input, unicode):
#        return input.encode('utf-8')
#    else:
#        return input


headers = ['uid', 'mid', 'reposts_count', 'comments_count', 'attitudes_count', 'text', 'retweeted_status', 'pic_infos', 'source', 'created_at', 'created_time', 'geo', 'deleted']

def last_deleted_weibos_to_csv(db, uid, del_time=None, out='weibos.csv'):
	if del_time is None:
		sql = 'select distinct deleted from status where uid=%s order by deleted desc limit 1' % uid
		del_time = db_util.execute(db, sql)[0]
	sql = ''
	for header in headers:
		sql += header
		sql += ', '
	sql = sql[:-2]
	sql = 'SELECT ' + sql + ' FROM status WHERE deleted=%d ORDER BY created_time' % (del_time)
	table_to_csv(db, sql, out, headers)

def all_weibos_to_csv(db, uid, out='weibos.csv'):
	sql = ''
	for header in headers:
		sql += header
		sql += ', '
	sql = sql[:-2]
	sql = 'SELECT ' + sql + ' FROM status WHERE uid=%s ORDER BY created_time' % uid
	table_to_csv(db, sql, out, headers)

def export_all(config):
	db = config['db']
	for entry in config['tasks']:
		uid = entry['uid']
		uname = entry['name']
		out = uname + '_all_' + time.strftime("%Y-%m-%d") + '.csv'
		all_weibos_to_csv(db, uid, out)
		logger.log('[x] Export %s\'s weibo to %s' % (uid, out), 'green')

def test():
	all_weibos_to_csv('t7.db', '3675868752', 'FXD_test.csv')

if __name__ == "__main__":
	test()