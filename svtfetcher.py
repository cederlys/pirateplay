#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Download shows from svtplay.
#
# Use
#
#    python svtfetcher.py --print-shows
#
# to get a list of the currently available shows.  Then, prepare a
# file named $HOME/.svtfetch that contains one line for each show you
# want to download.  Each line should contain the title as printed by
# the above command, followed by one or more spaces, followed by the
# directory where you want to store the episodes.  Blank lines are
# ignored, as are lines starting with "#".
#
# Once you have a .svtfetch file, use this command to automatically
# download all shows:
#
#    python svtfetcher.py --download
#
# Shows that are already downloaded will not be downloaded again,
# unless you have removed them.  Aborted downloads will have the
# extension ".tmp", and will be resumed if you re-run this program.
#
# A sample .svtfetch file might look like this:
#
#    tinga_tinga  /movies/children/tinga-tinga
#    timmy        /movies/children/timmy

import os
import re
import sys
import urllib2
import multiprocessing

import BeautifulSoup

import pirateplay

resume = False
PARALLELISM = 1

def load_series():
    global DIRS, TITLES

    DIRS = {}
    TITLES = []
    for line in open(os.path.join(os.getenv("HOME"), ".svtfetch")).readlines():
        line = line.strip()
        if len(line) == 0 or line[0] == "#":
            continue
        title, directory = line.split(" ", 1)
        title = title.strip()
        directory = directory.strip()
        DIRS[title] = directory.decode("utf-8")
        TITLES.append(title)

class Downloader(object):
    def __init__(self, exe, d, tmppath, fullpath):
        self.__exe = exe
        self.__d = d
        self.__tmppath = tmppath
        self.__fullpath = fullpath

    def __str__(self):
        return unicode(self).encode("utf-8")

    def execute(self):
        if os.path.exists(self.__fullpath.encode("utf-8")):
            print "Already downloaded", self.__fullpath.encode("utf-8")
            return
        size = None

        # Resume does not work if the file is too small.
        try:
            size = os.stat(self.__tmppath.encode("utf-8")).st_size
            print "Temporary file of size", size, ":", self.__tmppath.encode("utf-8")
        except OSError:
            pass
        if size is not None and (size < 1048576 or not resume):
            print "Unlinking", self.__tmppath.encode("utf-8")
            os.unlink(self.__tmppath.encode("utf-8"))

        print "Downloading", self.__fullpath.encode("utf-8")
        os.system((u"mkdir -p " + self.__d).encode('utf-8'))
        if os.system(self.__exe.encode('utf-8')) == 0:
            os.system((u"mv " + self.__tmppath + u" " + self.__fullpath)
                      .encode('utf-8'))

def cmdline(series, url, ignore_downloaded, execute):
    best = 0
    file = url.split("/")[-1]
    d = DIRS[series]
    fullpath = os.path.join(d, file + ".flv")
    if ignore_downloaded and os.path.exists(fullpath.encode("utf-8")):
        return None
    tmppath = fullpath + ".tmp"
    if os.path.exists(tmppath.encode("utf-8")):
        if resume:
            print "Resuming download:", fullpath.encode("utf-8")
        else:
            print "Restarting download:", fullpath.encode("utf-8")
    else:
        print "New download:", fullpath.encode("utf-8")

    best_alt = None
    all_cmds = pirateplay.generate_getcmd("http://www.svtplay.se" + url,
                                          False, output_file=tmppath)
    try:
        non_dups = pirateplay.remove_duplicates(all_cmds)
    except ValueError:
        print "Cannot find cmd for", fullpath
        return None
    bitrates = []
    for alt in non_dups:
        lines = alt.splitlines()
        m = re.search("quality: ([0-9]*)", lines[0])
        if not m:
            print "SKIPPING", alt
            continue
        q = int(m.group(1))
        bitrates.append(q)
        if q > best:
            best = q
            best_alt = alt

    if not best_alt:
        print "No bitrate match found for", url
        return None

    lines = best_alt.splitlines()
    exe = lines[1]
    if resume:
        exe = exe.replace(" ", " --resume ", 1)

    print "Selecting bitrate", best, "among", ', '.join(map(str,
                                                            sorted(bitrates)))

    if execute:
        return Downloader(exe, d, tmppath, fullpath)

    return exe

def getshows():
    print "Fetching shows"
    data = urllib2.urlopen("http://www.svtplay.se/alfabetisk").read()
    soup = BeautifulSoup.BeautifulSoup(data)
    shows = {}
    for a in soup.findAll("a", "playLetterLink"):
        [empty, title] = a["href"].split("/")
        shows[title] = a.string
    print "Found", len(shows), "shows"
    return shows

def getshow_urls(readable_title, title):
    print "Fetching %s (%s)" % (readable_title, title)
    urls = []
    url = "http://www.svtplay.se/" + title
    while True:
        print "Fetching", url
        try:
            data = urllib2.urlopen(url).read()
        except urllib2.HTTPError:
            print "FAILED to fetch", url
            break
        soup = BeautifulSoup.BeautifulSoup(data)
        pager_section = soup.find("div", "playPagerSections")
        if pager_section is None:
            break
        for a in pager_section.findAll("a", "playLink"):
            lnk = a["href"]
            # print a.find("h5").string.strip(), lnk
            urls = [lnk] + urls
        pager = soup.find("ul", "playLargePager")
        next_page = pager.find("a", "playPagerNext")
        if next_page is None or "disabled" in next_page["class"]:
            break
        url = "http://www.svtplay.se" + next_page["href"]
    print "Found", len(urls), "episodes"
    return urls

def run_download(data):
    print "Download", data[0], "of", queuesize
    data[1].execute()

def main():
    global queuesize

    args = sys.argv[1:]
    if len(args) == 0:
        print "Usage: series-fetcher { --print-shows | --download | --dry-run }\n"
        print "What to download is specified in ~/.svtfetch."
        return
    if args[0] == "--print-shows":
        shows = getshows().keys()
        shows.sort()
        for s in shows:
            print s
        return
    if args[0] == "--download":
        load_series()
        shows = getshows()
        queue = []
        for series in TITLES:
            if series not in shows:
                continue
            for url in getshow_urls(shows[series], series):
                downloader = cmdline(series, url, True, True)
                if downloader:
                    queue.append(downloader)
        queuesize = len(queue)
        if queuesize > 0:
            if PARALLELISM > 1:
                pool = multiprocessing.Pool(min(PARALLELISM, queuesize))
                pool.map(run_download, list(enumerate(queue)), 1)
                pool.close()
                pool.join()
            else:
                for data in enumerate(queue):
                    run_download(data)
        return
    if args[0] == "--dry-run":
        load_series()
        shows = getshows()
        for series in TITLES:
            if series not in shows:
                continue
            for url in getshow_urls(shows[series], series):
                print cmdline(series, url, False, False).encode('utf-8')
        return
    if args[0] == "--manual":
        load_series()
        downloader = cmdline(FIXME, args[1], True, True)
        if downloader:
            downloader.execute()
        else:
            sys.exit(1)
        return

if __name__ == '__main__':
    main()
