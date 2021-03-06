# -*- coding: utf-8 -*-
import datetime

import feedparser
from django import template


register = template.Library()


@register.inclusion_tag("feeds/pull_feeds.html")
def pull_feeds(url, max_count = 4):
	posts = []
	feed = feedparser.parse(url)
	entries_count = len(feed.entries)
	for i in range(min(max_count, entries_count)):
		try:
			pub_date = feed.entries[i].published_parsed
		except AttributeError:
			pub_date = feed.entries[i].updated_parsed
		published = datetime.date(pub_date[0], pub_date[1], pub_date[2])
		try:
			posts.append({
				'title': feed.entries[i].title,
				'link': feed.entries[i].link,
				'published': published,
			})
		except IndexError:
			pass
	return {'posts': posts}
