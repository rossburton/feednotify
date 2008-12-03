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
from xml.sax.saxutils import escape

# TODO: somehow add a "save for later" button which does... something.

pynotify.init("FeedNotify")

feedparser.USER_AGENT = "FeedNotify/%s +http://burtonini.com/" % VERSION

feeds = []

class Feed:
    def __init__(self, title, url):
        self.title = title
        self.url = url
        self.seen = set()
        self.etag = None
        self.modified = None

    def parse(self, feed):
        if feed.has_key("etag"):
            self.etag = feed.etag
        if feed.has_key("modified"):
            self.modified = feed.modified

        count = 0
        previous = self.seen.copy()

        for entry in feed.entries:
            if entry.id in previous:
                previous.remove(entry.id)
            else:
                self.seen.add(entry.id)
                # TODO: improve this to be the N most recent unseen posts
                if count < 5:
                    count = count + 1
                    message = "<a href='%s'>%s</a>" % (entry.link, escape(entry.title))
                    n = pynotify.Notification(self.title, message)
                    n.set_category("email.arrived")
                    n.set_urgency(0)
                    # TODO: Set icon to stock_news
                    n.show()

        # Now previous is the set of IDs which have falled out of the feed
        self.seen = self.seen - previous

    def run(self):
        feed = feedparser.parse(self.url, etag=self.etag, modified=self.modified)
        # TODO: handle errors and popup a error notification
        # Local feeds don't have a status
        if not feed.has_key("status"):
            self.parse(feed)
        # If there is a status field, handle it
        elif feed.status >= 200 and feed.status < 400:
            # Success and Redirection
            if feed.status == 304:
                # Not Modified, no-op
                pass
            elif feed.status == 301:
                # Moved Permanently
                self.url = feed.url
                self.parse(feed)
            else:
                # Everything else
                self.parse(feed)
        elif feed.status == 410:
            # Gone
            feeds.remove(feed)


if __name__ == "__main__":
    import sys, time

    if sys.argv[1:]:
        for url in sys.argv[1:]:
            feeds.append(Feed("Test", url))
    else:
        feeds.append(Feed("Guardian", "http://feeds.guardian.co.uk/theguardian/rss"))
        feeds.append(Feed("Comment Is Free", "http://feeds.guardian.co.uk/theguardian/commentisfree/rss"))
    print feeds

    while True:
        [feed.run() for feed in feeds]
        time.sleep(5 * 60)
