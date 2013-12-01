#!/bin/env python

import os
import sqlite3
import ConfigParser

# config parse
config = ConfigParser.ConfigParser()
config.read('build.ini')


# inner helper
def _c(key, section = 'main'):
    return config.get(section, key)

def _indexAdd(db, name, type, path):
    if (db):
        db.execute(SQL_INDEX_ADD % (name, type, path))



# static var
SQL_INDEX_ADD = _c('index_add', 'sql')



print 'init database'
# sql import
fp = open(_c('file_sql'), 'r')
sqls = fp.read().split("\r")
fp.close()

# db init
conn = sqlite3.connect(_c('file_db'))
cur = conn.cursor()

# table init
cur.execute(_c('table_drop', 'sql'))
cur.execute(_c('table_create', 'sql'))
cur.execute(_c('index_create', 'sql'))

# sql exec
for sql in sqls:
    ret = sql.split('|')
    _indexAdd(cur, ret[2], ret[0], ret[1])

# db close
conn.commit()
conn.close()






# create index.html
print 'output index.html'
os.system('cp ' + _c('file_sheet') + ' ' + _c('file_index'));

# copy static resource
print 'output *.css'
os.system('cp ' + _c('dir_src') + '/*.css ' + _c('dir_document'))

# make icon.png
print 'output icon.png'
os.system('sips -z 32 32 ' + _c('file_logo') + ' --out ' + _c('file_icon') + ' >> /dev/null')

# make archived docset
print 'output tgz'
os.system("tar --exclude='.DS_Store' -cvzf " + _c('file_tgz') + " " + _c('file_docset'))

print "complete"
