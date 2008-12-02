#! /usr/bin/env python

import feedparser, time, pynotify

# TODO: somehow add a "save for later" button which does... something.

pynotify.init("FeedNotify")

class Feed:
    def __init__(self, title, url):
        self.title = title
        self.url = url
        # TODO: copy the seen set each run and then remove IDs we get so that old IDs
        # can be removed from the persistant set
        self.seen = set()
        self.etag = None
        self.modified = None

    def run(self):
        feed = feedparser.parse(self.url, etag=self.etag, modified=self.modified)
        if feed.status == 200:
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

feeds = (
    Feed("Guardian", "http://feeds.guardian.co.uk/theguardian/rss"),
    Feed("Comment Is Free", "http://feeds.guardian.co.uk/theguardian/commentisfree/rss"),
)

while True:
    [feed.run() for feed in feeds]
