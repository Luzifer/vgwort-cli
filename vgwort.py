#!/usr/bin/env python

###
# Requirements:
# * Install sqlite3 and BeautifulSoup modules using PIP
# * Get litepiesql from http://www.kipdola.be/en/blog/skerit/131-introducing-litepiesql-python-sqlite
#   and put it into your python path (most likely next to this script)
###
# Usage: Ask for help using 'vgwort.py -h'
###
# "THE COFFEE-WARE LICENSE" (Revision 42):
# <knut@ahlers.me> wrote this file. As long as you retain this notice you
# can do whatever you want with this stuff. If we meet some day, and you think
# this stuff is worth it, you can buy me a coffee in return. --Knut
###

import litepiesql, sqlite3, urllib2, argparse, os, sys, re
from BeautifulSoup import BeautifulSoup

def main():
  parser = argparse.ArgumentParser(description = 'Local management of VGWort counter marks')
  parser.add_argument('--add-marks', help='Parse csv export of counter marks', metavar='<CSV Document>')
  parser.add_argument('--get-unused', action='store_true', help='Get one unused counter mark')
  parser.add_argument('--refresh-used-marks', help='Scans sitemap.xml for articles using counter marks', metavar='<URL to sitemap.xml>')
  parser.add_argument('--get-url-for-mark', help='Displays found URL for given counter mark', metavar='[mark, [...]]', nargs='*')
  args = parser.parse_args()

  vgw = VGWort(os.path.expanduser('~/.vgwort.db'))

  if args.add_marks:
    vgw.add_marks_from_csv(args.add_marks)

  if args.get_unused:
    vgw.get_unused_mark()

  if args.refresh_used_marks:
    vgw.refresh_used_marks(args.refresh_used_marks)

  if args.get_url_for_mark is not None:
    vgw.get_url_for_mark(args.get_url_for_mark)

def progressbar(it, prefix = "", size = 60):
  count = len(it)
  def _show(_i):
    x = int(size*_i/count)
    sys.stdout.write("%s[%s%s] %i/%i\r" % (prefix, "#"*x, "."*(size-x), _i, count))
    sys.stdout.flush()
  
  _show(0)
  for i, item in enumerate(it):
    yield item
    _show(i+1)
  sys.stdout.write("\n")
  sys.stdout.flush()

class VGWort:
  def __init__(self, databasefile):
    self._load_store(databasefile)

  def _err(self, string):
    print 'ERR: %s' % string
    sys.exit(1)

  def _load_store(self, databasefile):
    require_init = False
    if not os.path.exists(databasefile):
      require_init = True
    self.database = litepiesql.Database(databasefile)

    if require_init:
      self.database.query('CREATE TABLE marks ( MarkerURL VARCHAR(255) UNIQUE, PrivateKey VARCHAR(40), BlogURL VARCHAR(255), FoundOn DATE );')

  def add_marks_from_csv(self, csvfile):
    if not os.path.exists(csvfile):
      self._err('ERR: Import file %s does not exist.' % csvfile)

    imported = 0

    lines = open(csvfile, 'r').read().split('\n')
    while len(lines) > 0:
      line = lines.pop(0)
      if line[0] == ';':
        continue
      data = {}
      data['MarkerURL'] = re.findall('(http[^"]+)"', line.split(';')[1])[0]
      data['PrivateKey'] = lines.pop(0).split(';')[2]
      try:
        self.database.insert('marks', data)
        imported = imported + 1
      except sqlite3.IntegrityError:
        continue

    print 'Successfully imported %d counter marks' % imported

  def get_unused_mark(self):
    data = self.database.query("SELECT * FROM marks WHERE BlogURL IS NULL LIMIT 1")
    print 'Unused counter mark: %s' % data[0]['markerurl']

  def refresh_used_marks(self, sitemap_url):
    soup = BeautifulSoup(urllib2.urlopen(sitemap_url).read())
    urls = soup.findAll('url')
    for url in progressbar(urls, 'Searching URLs:'):
      sitedata = urllib2.urlopen(url.loc.text).read()
      matches = re.findall('http://vg[0-9]+\.met\.vgwort\.de/na/[a-z0-9]{32}', sitedata)
      if len(matches) == 0:
        continue
      self.database.update('marks', {'BlogURL': url.loc.text, 'FoundOn': 'now()'}, 'MarkerURL = "%s"' % matches[0])

  def get_url_for_mark(self, marks):
    data = []
    if len(marks) == 0:
      data = self.database.query('SELECT * FROM marks WHERE BlogURL IS NOT NULL')
    else:
      for mark in marks:
        d = self.database.query("SELECT * FROM marks WHERE MarkerURL LIKE '%%%s%%' OR PrivateKey = '%s'" % (mark, mark))
        for i in d:
          data.append(i)

    for d in data:
      print '%s => %s' % (d['privatekey'], d['blogurl'])


if __name__ == '__main__':
  main()
