#! /usr/bin/env python

# Copyright (C) 2008 Ross Burton <ross@burtonini.com>
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51 Franklin
# St, Fifth Floor, Boston, MA 02110-1301 USA

VERSION="0.1"

import feedparser, pynotify

# TODO: somehow add a "save for later" button which does... something.

pynotify.init("FeedNotify")

feedparser.USER_AGENT = "FeedNotify/%s +http://burtonini.com/" % VERSION

feeds = []

class Feed:
    def __init__(self, title, url):
        self.title = title
        self.url = url
        # TODO: copy the seen set each run and then remove IDs we get so that old IDs
        # can be removed from the persistant set
        self.seen = set()
        self.etag = None
        self.modified = None

    def parse(self, feed):
        self.etag = feed.etag
        self.modified = feed.modified
        count = 0

        for entry in feed.entries:
            if entry.id not in self.seen:
                self.seen.add(entry.id)
                    # TODO: improve this to be the N most recent unseen posts
                if count < 5:
                    count = count + 1
                    message = "<a href='%s'>%s</a>" % (entry.link, entry.title)
                    n = pynotify.Notification(self.title, message)
                    n.set_category("email.arrived")
                    n.set_urgency(0)
                    n.show()

    def run(self):
        feed = feedparser.parse(self.url, etag=self.etag, modified=self.modified)
        # TODO: handle errors and popup a error notification
        if feed.status == 200:
            # OK
            self.parse(feed)
        elif feed.status == 301:
            # Moved Permanently
            self.url = feed.url
            self.parse(feed)
        elif feed.status == 401:
            # Gone
            del feeds[feed]

feeds.append(Feed("Guardian", "http://feeds.guardian.co.uk/theguardian/rss"))
feeds.append(Feed("Comment Is Free", "http://feeds.guardian.co.uk/theguardian/commentisfree/rss"))

if __name__ == "__main__":
    import time
    while True:
        [feed.run() for feed in feeds]
        time.sleep(5 * 60)
