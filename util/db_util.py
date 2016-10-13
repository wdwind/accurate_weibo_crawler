import sqlite3

def execute(db, sql, entry=None):
    conn = sqlite3.connect(db)
    c = conn.cursor()
    #rows = c.execute(sql)
    #try:
    #    for r in rows:
    #        values.append(r)
    #except:
    #    pass
    if entry is None:
        c.execute(sql)
    else:
        c.execute(sql, entry)
    rows = c.fetchall()
    conn.commit()
    conn.close()
    return rows

def executemany(db, sql, entries=None):
    conn = sqlite3.connect(db)
    c = conn.cursor()
    if entries is None:
        c.executemany(sql)
    else:
        c.executemany(sql, entries)
    rows = c.fetchall()
    conn.commit()
    conn.close()
    return rows

def get_table_structure(db, table):
    """ 
       Returns a list of tuples with column informations:
      (id, name, type, notnull, default_value, primary_key)
    """
    s = []
    conn = sqlite3.connect(db)
    sql = "pragma table_info('" + table + "')"
    for row in conn.execute(sql).fetchall():
        s.append(row)
    conn.close()
    return s

def get_table_create(db, table):
    s = get_table_structure(db, table)
    sql = ''
    for col in s:
        sql += col[1]
        sql += ' '
        sql += col[2]
        if col[5] == 1:
            sql += ' primary key'
        sql += ', '
    sql = sql[:-2]
    sql = 'CREATE TABLE ' + table + ' (' + sql + ')'
    return sql

def print_table(db, table):
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute("SELECT * FROM " + table)
    data = c.fetchall()
    print __pp(c, data)
    #print(c.fetchall())
    conn.commit()
    conn.close()

def __pp(cursor, data=None, rowlens=0):
    """
    Pretty Printing of Database Cursor Contents

    """
    d = cursor.description
    if not d:
        return "#### NO RESULTS ###"
    names = []
    lengths = []
    rules = []
    if not data:
        t = cursor.fetchall()
    for dd in d:    # iterate over description
        l = dd[1]
        if not l:
            l = 12             # or default arg ...
        l = max(l, len(dd[0])) # handle long names
        names.append(dd[0])
        lengths.append(l)
    for col in range(len(lengths)):
        if rowlens:
            rls = [len(str(row[col])) for row in data if row[col]]
            lengths[col] = max([lengths[col]]+rls)
        rules.append("-"*lengths[col])
    format = " ".join(["%%-%ss" % l for l in lengths])
    result = [format % tuple(names)]
    result.append(format % tuple(rules))
    for row in data:
        result.append(format % row)
    return "\n".join(result)


def drop_table(db, table):
    """
    Drop one table.
    
    """
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute('DROP TABLE IF EXISTS ' + table)
    conn.commit()
    conn.close()

# http://stackoverflow.com/a/18054751/4214478
def get_rows_as_json(db, sql, entry=None):
    conn = sqlite3.connect(db)
    conn.row_factory = sqlite3.Row # This enables column access by name: row['column_name'] 
    db = conn.cursor()

    if entry is None:
        rows = db.execute(sql).fetchall()
    else:
        rows = db.execute(sql, entry).fetchall()

    conn.commit()
    conn.close()

    return [dict(ix) for ix in rows]
    #if json_str:
    #    return json.dumps( [dict(ix) for ix in rows] ) #CREATE JSON
    #return rows

def generate_create_sql(table, columns):
	sql = ""
	for key in columns:
		sql += key
		sql += ' '
		sql += columns[key]
		sql += ', '
	sql = sql[:-2]
	sql = 'CREATE TABLE ' + table + ' (' + sql + ')'
	return sql

def generate_insert_sql(table, columns):
	sql = ""
	for key in columns:
		sql += '?, '
	sql = sql[:-2]
	sql = 'INSERT INTO ' + table + ' VALUES (' + sql + ')'
	return sql

def generate_update_sql(table, columns):
	sql = ""
	for key in columns:
		sql += key + '=?, '
	sql = sql[:-2]
	sql = 'UPDATE ' + table + ' SET ' + sql + ' WHERE id=?'
	return sql

def generate_insert_update_sql(table, columns):
	keys = ''
	values = ''
	for key in columns:
		keys += key + ', '
		values += '?, '
	keys = keys[:-2]
	values = values[:-2]
	
	sql = 'INSERT OR REPLACE INTO ' + table + ' (' + keys + ') VALUES (' + values + ');'
	return sql