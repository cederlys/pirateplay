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

    def execute(self):
        if os.path.exists(self.__fullpath):
            print "Already downloaded", self.__fullpath
            return
        size = None

        # Resume does not work if the file is too small.
        try:
            size = os.stat(self.__tmppath).st_size
            print "Temporary file of size", size, ":", self.__tmppath
        except OSError:
            pass
        if size is not None and size < 1048576:
            print "Unlinking", self.__tmppath
            os.unlink(self.__tmppath)

        print "Downloading", self.__fullpath
        os.system((u"mkdir -p " + self.__d).encode('utf-8'))
        if os.system(self.__exe.encode('utf-8')) == 0:
            os.system((u"mv " + self.__tmppath + u" " + self.__fullpath)
                      .encode('utf-8'))

def cmdline(url, ignore_downloaded, execute):
    best = 0
    m = re.search("svtplay.se/[^/]+/[^/]+/([^/]+)/([^/?]+)", url)
    series = m.group(1)
    file = m.group(2)
    d = DIRS[series]
    fullpath = os.path.join(d, file + ".mp4")
    if ignore_downloaded and os.path.exists(fullpath):
        return None
    tmppath = fullpath + ".tmp"
    if os.path.exists(tmppath):
        print "Resuming download:", fullpath
    else:
        print "New download:", fullpath

    best_alt = None
    all_cmds = pirateplay.generate_getcmd(url, False, output_file=tmppath)
    try:
        non_dups = pirateplay.remove_duplicates(all_cmds)
    except ValueError:
        print "Cannot find cmd for", fullpath
        return None
    bitrates = []
    for alt in non_dups:
        m = re.search("quality: ([0-9]*) kbps", alt)
        if not m:
            print "SKIPPING", alt
            continue
        q = int(m.group(1))
        bitrates.append(q)
        if q > best:
            best = q
            best_alt = alt

    if not best_alt:
        print "No match found for", url
        return None

    exe = best_alt.splitlines()[1]
    exe = exe.replace(" ", " --resume ", 1)

    print "Selecting bitrate", best, "among", ', '.join(map(str,
                                                            sorted(bitrates)))

    if execute:
        return Downloader(exe, d, tmppath, fullpath)

    return exe

def getshows():
    print "Fetching shows"
    data = urllib2.urlopen("http://svtplay.se/alfabetisk").read()
    soup = BeautifulSoup.BeautifulSoup(data)
    shows = {}
    for ul in soup.findAll("ul", "leter-list"):
        for li in ul.findAll('li', recursive=False):
            for a in li.findAll('a', recursive=False):
                [empty, t, nr, title] = a["href"].split("/")
                shows[title] = nr
    print "Found", len(shows), "shows"
    return shows

def getshow_urls(nr, title):
    print "Fetching", title
    url = "http://feeds.svtplay.se/v1/video/list/" + nr + "/" + title + "?expression=full"
    data = urllib2.urlopen(url).read()
    soup = BeautifulSoup.BeautifulStoneSoup(data)
    urls = []
    for i in soup.findAll("item"):
        lnk = i.find("link").string.encode("ascii")
        if re.search("teckentolkad", lnk):
            continue
        urls = [lnk] + urls
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
                downloader = cmdline(url, True, True)
                if downloader:
                    queue.append(downloader)
        queuesize = len(queue)
        if queuesize > 0:
            pool = multiprocessing.Pool(min(7, queuesize))
            pool.map(run_download, list(enumerate(queue)), 1)
            pool.close()
            pool.join()
        return
    if args[0] == "--dry-run":
        load_series()
        shows = getshows()
        for series in TITLES:
            for url in getshow_urls(shows[series], series):
                print cmdline(url, False, False).encode('utf-8')
        return

if __name__ == '__main__':
    main()
