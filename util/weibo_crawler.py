# -*- coding: utf-8 -*-

import time
import json
import logger
import sys
import db_util
import weibo_util
import time_util
import weibo_writer

class WeiboCrawler(object):

    TABLES = {'user_info' : './tables/user_info.json',
              'status' : './tables/status.json'}

    def __init__(self, config):
        self.conf = config
        self.wids = None
        self.create_tables()

    def create_tables(self):
        for table in WeiboCrawler.TABLES:
            domains = WeiboCrawler.get_table_domains(table)
            sql = db_util.generate_create_sql(table, domains)
            try:
                db_util.execute(self.conf['db'], sql)
                logger.log('[x] Table `%s` created!' % (table), 'green')
            except:
                logger.log('[x] Table `%s` already exsits' % (table))

    def update(self):
        logger.log('[x] Crawling...')
        for task in self.conf['tasks']:
            # logger.log('[x] Update user %s, name %s' % (task['uid'], task['name']))
            sql = 'SELECT statuses_count FROM user_info WHERE id=? ORDER BY update_time desc LIMIT 1'
            basic_info = db_util.execute(self.conf['db'], sql, [task['uid']])
            self.update_timeline(task, len(basic_info) == 0)

    def update_timeline(self, task, new_user):
        uid = task['uid']

        user_info = weibo_util.user_info(uid)
        num_weibos = int(user_info['statuses_count'])

        old_weibos = self.get_old_weibos(new_user, uid)
        since_id = 0 if old_weibos == {} else min(old_weibos.keys())
        all_weibos = self.get_all_weibos(uid, num_weibos, max_id=0, since_id=since_id)
        new_weibos = {wid : all_weibos[wid] for wid in all_weibos if wid not in old_weibos}
        deleted_weibos = {wid : old_weibos[wid] for wid in old_weibos if wid not in all_weibos}

        if len(all_weibos) != num_weibos:
            deleted_weibos = self.check_deleted_weibos(deleted_weibos)

        self.update_all(task, user_info, all_weibos, new_weibos, deleted_weibos)
        #logger.log('[x] Crawl finished for user %s.' % (uid))

    def get_old_weibos(self, new_user, uid):
        if new_user:
            return {}
        else:
            sql = 'SELECT * FROM status WHERE deleted=-1 AND uid=? ORDER BY id desc'
            old_weibos = db_util.get_rows_as_dict(self.conf['db'], sql, [uid])
            results = {}
            for weibo in old_weibos:
                temp = {k: (json.loads(weibo[k]) if type(weibo[k]) == unicode else weibo[k]) for k in weibo}
                results[temp['id']] = temp
            return results

    def get_all_weibos(self, uid, num_weibos, max_id, since_id):
        all_weibos = {}
        all_weibos = weibo_util.user_timeline_all(uid, num_weibos, all_weibos, weibo_util.user_timeline_public)
        times = 0
        while len(all_weibos) != num_weibos:
            logger.log('[x] Crawling... %d/%d' % (len(all_weibos), num_weibos))
            all_weibos = weibo_util.user_timeline_all(uid, num_weibos, all_weibos, weibo_util.user_timeline_public, count=200)
            times += 1
            if times == 2:
                break
        times = 0
        while len(all_weibos) != num_weibos:
            logger.log('[x] Crawling... %d/%d' % (len(all_weibos), num_weibos))
            all_weibos = weibo_util.user_timeline_all(uid, num_weibos, all_weibos, weibo_util.user_timeline_private)
            times += 1
            if times == 1:
                break
        times = 0
        while len(all_weibos) != num_weibos:
            logger.log('[x] Crawling... %d/%d' % (len(all_weibos), num_weibos))
            all_weibos = weibo_util.user_timeline_all_since(uid, since_id, num_weibos, all_weibos, weibo_util.user_timeline_public, count=200)
            times += 1
            if times == 2:
                break
        # comment this part because the `since_id` argument does not work in private api
        #times = 0
        #while len(all_weibos) != num_weibos:
        #    logger.log('[x] Crawling... %d/%d' % (len(all_weibos), num_weibos))
        #    all_weibos = weibo_util.user_timeline_all_since(uid, since_id, num_weibos, all_weibos, weibo_util.user_timeline_private)
        #    times += 1
        #    if times == 1:
        #        break
        logger.log('[x] Crawling... %d/%d' % (len(all_weibos), num_weibos))
        return all_weibos

    def check_deleted_weibos(self, deleted_weibos):
        if len(deleted_weibos) == 0: return deleted_weibos
        for wid in deleted_weibos:
            for _ in range(3):
                if weibo_util.weibo(wid) != None:
                    del deleted_weibos[wid]
                    break
            if wid not in deleted_weibos:
                continue
            mid = deleted_weibos[wid]['mid']
            if weibo_util.weibo_exists(mid) is True:
                del deleted_weibos[wid]
        return deleted_weibos

    def update_all(self, task, user_info, all_weibos, new_weibos, deleted_weibos):
        deleted_time = self.update_deletion(deleted_weibos.values())
        if deleted_time != -1:
            out = task['name']+'_del_' + time.strftime("%Y-%m-%d_%H.%M.%S") + '.csv'
            weibo_writer.last_deleted_weibos_to_csv(self.conf['db'], task['uid'], \
                deleted_time, out)
            logger.log('[x] %s\'s deleted weibos are exported to %s' % (task['uid'], out), 'green')
        self.show_user_info(user_info)
        self.show_user_weibos(new_weibos.values(), deleted=False)
        self.show_user_weibos(deleted_weibos.values(), deleted=True)
        self.insert_table(table='user_info', entries=[user_info])
        self.update_table(table='status', entries=all_weibos.values(), delete=False)

    # helper functions
    def show_user_info(self, user_info):
        logger.log(u'[x] User: %s, following: %d, follower: %d, weibo: %d' \
            %(user_info['screen_name'], \
                int(user_info['friends_count']), \
                int(user_info['followers_count']), \
                int(user_info['statuses_count'])), 'green')

    def show_user_weibos(self, weibos, deleted=False):
        if deleted is False:
            logger.log('[x] %d weibos are created!' % len(weibos), 'green')
        else:
            logger.log('[x] %d weibos are deleted!' % len(weibos), 'red')
        id = 1
        for weibo in weibos:
            logger.log('[x] Weibo %d:' % id)
            logger.log('[x]    URL: http://www.weibo.com/%s/%s' % (weibo['uid'], weibo['mid']))
            logger.log('[x]    Content: %s' % (weibo['text']))
            logger.log('[x]    Created at: %s' % (weibo['created_at']))
            logger.log('[x]    Repost count: %s' % (weibo['reposts_count']))
            logger.log('[x]    Comments count: %s' % (weibo['comments_count']))
            logger.log('[x]    Like count: %s' % (weibo['attitudes_count']))
            id += 1

    def insert_table(self, table, entries):
        if entries is None or len(entries) == 0:
            return
        domains = WeiboCrawler.get_table_domains(table)
        sql = db_util.generate_insert_sql(table, domains)
        entries = WeiboCrawler.json_to_entries(entries, domains)
        db_util.executemany(self.conf['db'], sql, entries)

    def update_table(self, table, entries, delete=False):
        if entries is None or len(entries) == 0:
            return
        domains = WeiboCrawler.get_table_domains(table)
        sql = db_util.generate_insert_update_sql(table, domains)
        entries = WeiboCrawler.json_to_entries(entries, domains)
        db_util.executemany(self.conf['db'], sql, entries)

    def update_deletion(self, deleted_weibos):
        if deleted_weibos is None or len(deleted_weibos) == 0:
            return -1
        uid = str(deleted_weibos[0]['uid'])
        unix_now = time_util.get_current_unix_time()
        delete_sql = "UPDATE status SET deleted=? WHERE id=?"
        entries = []
        for weibo in deleted_weibos:
            entries.append([unix_now, weibo['id']])
        db_util.executemany(self.conf['db'], delete_sql, entries)
        #weibo_writer.last_deleted_weibos_to_csv(self.conf['db'], uid, \
        #    unix_now, uid+'_del_'+str(unix_now)+'.csv')
        return unix_now

    @staticmethod
    def json_to_entries(items, domains):
        #items = byteify(items)
        entries = []
        for item in items:
            entry = []
            for key in domains:
                if key == 'deleted':
                    value = -1
                elif key == 'update_time':
                    value = time_util.get_current_unix_time()
                elif key == 'created_time':
                    value = time_util.parse_time_string(item['created_at'])
                elif key in item:
                    value = json.dumps(item[key])
                    if 'integer' in domains[key]:
                        value = long(value)
                else:
                    if 'integer' in domains[key]:
                        value = 0
                    else:
                        value = '""'
                entry.append(value)
            entries.append(entry)
        return entries

    @staticmethod
    def get_table_domains(table):
        domains = {}
        with open(WeiboCrawler.TABLES[table], 'rb') as file:
            domains.update(json.load(file))
        return domains

if __name__ == "__main__":
    pass