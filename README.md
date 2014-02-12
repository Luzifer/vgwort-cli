# Luzifer / vgwort-cli

This scripts helps you to manage your VGWort counter marks by using a little sqlite3 database placed into your home directory. It is able to import the CSV file from VGWort, search an unused mark for you and scan your blog using the sitemap.xml for used counter marks.

## Requirements

- Install `sqlite3` and `BeautifulSoup` modules using PIP

## Usage

```
$ ./vgwort.py -h
usage: vgwort.py [-h] [--add-marks <CSV Document>] [--get-unused]
                 [--refresh-used-marks <URL to sitemap.xml>]
                 [--get-url-for-mark [[mark, [...]] [[mark, [...]] ...]]]

Local management of VGWort counter marks

optional arguments:
  -h, --help            show this help message and exit
  --add-marks <CSV Document>
                        Parse csv export of counter marks
  --get-unused          Get one unused counter mark
  --refresh-used-marks <URL to sitemap.xml>
                        Scans sitemap.xml for articles using counter marks
  --get-url-for-mark [[mark, [...]] [[mark, [...]] ...]]
                        Displays found URL for given counter mark
```

## License

```
"THE COFFEE-WARE LICENSE" (Revision 42):
<knut@ahlers.me> wrote this file. As long as you retain this notice you
can do whatever you want with this stuff. If we meet some day, and you think
this stuff is worth it, you can buy me a coffee in return. --Knut
```
