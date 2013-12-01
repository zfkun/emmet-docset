#!/bin/env python

import os
import re
import sqlite3
import HTMLParser


# Section HTMLParser Class
class SectionHTMLParser(HTMLParser.HTMLParser):
    def __init__(self):
        HTMLParser.HTMLParser.__init__(self)
        self.inTag = 0
        self.inEnd = 0
        self.innerHTML = ''
        self.matches = []

    def addpendData(self, data):
        self.innerHTML += data
        # print 'innerHTML: ', self.innerHTML

    def handle_starttag(self, tag, attrs):
        if self.inTag > 0:
            if tag == 'section':
                self.inEnd += 1
                # print 'Start tag: ', tag, self.inTag , self.inEnd
            
            self.addpendData('<' + tag)
            
            for name, val in attrs:
                self.addpendData(' ' + name + '="' + val + '"')
            
            self.addpendData('>')
        else:
            if tag == 'section':
                for name, val in attrs:
                    if name == 'class':
                        vals = val.split(' ')
                        if 'ch-section' in vals:
                            self.inEnd += 1
                            self.inTag = 1
                            # print 'Begin Target', tag, attrs

    def handle_endtag(self, tag):
        if self.inTag:
            if tag == 'section':
                self.inEnd -= 1
                # print 'End tag: ', tag, self.inTag, self.inEnd

            if tag == 'section' and self.inEnd == 0:
                # print 'End Target: ', tag
                self.matches.append(self.innerHTML)
                self.inTag = 0
                self.inEnd = 0
                self.innerHTML = ''
            else:
                self.addpendData('</' + tag + '>')

    def handle_data(self, data):
        if self.inTag > 0 and self.inEnd > 0:
            self.addpendData(data)



class Config():
    RE_CATEGORY = r'<h2 class="ch-section__title">(.*?)</h2>'
    RE_SECTION = r'<h3 class="ch-subsection__title">(.*?)</h3>'
    RE_DIRECTIVE = r'<dt class="ch-snippet__name">(.*?)</dt>'

    NAME_DOCSET = 'Emmet'

    DIR_SRC = 'src/'
    DIR_PATCH = 'patch/'
    DIR_DOCSET = 'Emmet.docset/'
    DIR_DOCUMENT = 'Emmet.docset/Contents/Resources/Documents/'
    
    FILE_CHEATSHEET = 'src/cheat-sheet.html'
    FILE_DB = 'Emmet.docset/Contents/Resources/docSet.dsidx'

    SQL_TABLE_DROP = 'DROP TABLE IF EXISTS searchIndex'
    SQL_TABLE_CREAT = 'CREATE TABLE searchIndex(id INTEGER PRIMARY KEY, name TEXT, type TEXT, path TEXT)'
    SQL_INDEX_CREAT = 'CREATE UNIQUE INDEX anchor ON searchIndex (name, type, path)'
    SQL_INDEX_ADD = "insert into searchIndex(name, type, path) values('%s', '%s', 'index.html#%s')"



def getRule(type):
    if (type == 'Category'):
        return Config.RE_CATEGORY
    elif (type == 'Section'):
        return Config.RE_SECTION
    elif (type == 'Directive'):
        return Config.RE_DIRECTIVE
    else:
        return ''

def indexAdd(db, name, type, path):
    if (db):
        db.execute(Config.SQL_INDEX_ADD % (name, type, path))

def indexAddByCategory(db, data, category, type):  
    for r in re.findall(getRule(type), data, re.S):
        r = re.compile('\s{1,}').sub(' ', r)
        # print '(name, type, path): ', r, ',', type, ',', type + '_' + category + '_' + r
        indexAdd(db, r, type, type + '_' + category + '_' + r)





# database
conn = sqlite3.connect(Config.FILE_DB)
cur = conn.cursor()

# Create Table
cur.execute(Config.SQL_TABLE_DROP)
cur.execute(Config.SQL_TABLE_CREAT)
cur.execute(Config.SQL_INDEX_CREAT)



# html
fp = open(Config.FILE_CHEATSHEET, 'r')
html = fp.read()
fp.close()


# html parser
parser = SectionHTMLParser()
parser.feed(html)


# db init
for data in parser.matches:
    ret = re.findall(Config.RE_CATEGORY, data, re.S)
    category = ret[0]

    print 'Init Category >>> ', category
    
    # Category init
    indexAdd(cur, category.lower(), 'Category', 'Category_' + category)

    # Section init
    indexAddByCategory(cur, data, category, 'Section')

    # Directive init
    if (category.lower() != 'syntax'):
        indexAddByCategory(cur, data, category, 'Directive')


# db close
conn.commit()
conn.close()






# create index.html with patch
os.system('cat ' + Config.FILE_CHEATSHEET + ' ' + Config.DIR_PATCH + 'index.patch >> ' + Config.DIR_DOCUMENT + 'index.html');

# copy static resource
os.system('cp src/*.css ' + Config.DIR_DOCUMENT)

# make icon.png
os.system('sips -z 32 32 ' + Config.DIR_SRC + 'logo.png --out ' + Config.DIR_DOCSET + 'icon.png')

# make archived docset
os.system("tar --exclude='.DS_Store' -cvzf " + Config.NAME_DOCSET + ".tgz " + Config.NAME_DOCSET + ".docset")
