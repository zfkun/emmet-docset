#!/bin/env python

import sqlite3
import re
import HTMLParser
import shutil


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

    DIR_SRC = 'src/'
    DIR_PATCH = 'patch/'
    DIR_DOCUMENT = 'Emmet.docset/Contents/Resources/Documents/'
    
    FILE_DB = 'Emmet.docset/Contents/Resources/docSet.dsidx'



def getRule(type):
    if (type == 'Category'):
        return Config.RE_CATEGORY
    elif (type == 'Section'):
        return Config.RE_SECTION
    elif (type == 'Directive'):
        return Config.RE_DIRECTIVE
    else:
        return ''


def indexInsert(db, data, category, type):  
    ret = re.findall(getRule(type), data, re.S)
    for r in ret:
        r = re.compile('\s{1,}').sub(' ', r)
        # print '(name, type, path): ', r, ',', type, ',', type + '_' + category + '_' + r
        db.execute("insert into searchIndex(name, type, path) values('%s', '%s', 'index.html#%s')" % (r, type, type + '_' + category + '_' + r))






# database
conn = sqlite3.connect(Config.FILE_DB)
cur = conn.cursor()

# Create Table
cur.execute('DROP TABLE IF EXISTS searchIndex')
cur.execute('CREATE TABLE searchIndex(id INTEGER PRIMARY KEY, name TEXT, type TEXT, path TEXT)')
cur.execute('CREATE UNIQUE INDEX anchor ON searchIndex (name, type, path)')



# html
fp = open(Config.DIR_SRC + 'cheat-sheet.html', 'r')
html = fp.read()
fp.close()


# html parser
parser = SectionHTMLParser()
parser.feed(html)


# db init
for data in parser.matches:
    ret = re.findall(Config.RE_SECTION_TITLE, data, re.S)
    category = ret[0]
    type = 'Category'
    print 'Init Category >>> ', category
    
    # Category init
    cur.execute("insert into searchIndex(name, type, path) values('%s', '%s', 'index.html#%s')" % (category.lower(), type, type + '_' + category))

    # Section init
    indexInsert(cur, data, category, 'Section')

    # Directive init
    if (category.lower() != 'syntax'):
        indexInsert(cur, data, category, 'Directive')


# db close
conn.commit()
conn.close()


# get patch code (JS)
fp = open(Config.DIR_PATCH + 'index.js', 'r')
patch = fp.read()
fp.close()

# create index.html
fp = open(Config.DIR_DOCUMENT + 'index.html', 'w')
fp.write(html + '<script>' + patch + '</script>')
fp.close()

# copy static resource
for css in ['main', 'cheatsheet']:
    shutil.copy(Config.DIR_SRC + css + '.css', Config.DIR_DOCUMENT)
