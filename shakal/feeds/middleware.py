# -*- coding: utf-8 -*-
#
from shakal.article.feeds import ArticleFeed
from shakal.forum.feeds import TopicFeed
from shakal.feeds import register_feed

class FeedsMiddleware(object):
	def process_request(self, request):
		setattr(request, '_feeds', [])
		register_feed(request, ArticleFeed)
		register_feed(request, TopicFeed)
