#! /usr/bin/env python

import feedparser, time, pynotify

# TODO: add a Feed abstraction with a title and URL

# TODO: somehow add a "save for later" button which does... something.

# TODO: copy the seen set each run and then remove IDs we get so that old IDs
# can be removed from the persistant set
seen = set()
etag = None
modified = None

pynotify.init("FeedNotify")

while True:
    feed = feedparser.parse("http://feeds.guardian.co.uk/theguardian/rss", etag=etag, modified=modified)
    if feed.status == 200:
        etag = feed.etag
        modified = feed.modified
        count = 0

        for entry in feed.entries:
            if entry.id not in seen:
                seen.add(entry.id)
                # TODO: improve this to be the N most recent unseen posts
                if count < 5:
                    count = count + 1
                    message = "<a href='%s'>%s</a>" % (entry.link, entry.title)
                    n = pynotify.Notification("Latest News", message)
                    n.set_category("email.arrived")
                    n.set_urgency(0)
                    n.show()
    time.sleep(60)
