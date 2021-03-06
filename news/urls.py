# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url

import feeds as news_feeds
import views as news_views


class Patterns(object):
	def __init__(self):
		self.app_name = 'news'
		self.name = 'news'

	@property
	def urls(self):
		urlpatterns = patterns('',
			url(r'^detail/(?P<slug>[-\w]+)/$', news_views.NewsDetailView.as_view(), name = "detail-by-slug"),
			url(r'^pridat/$', news_views.NewsCreateView.as_view(), name = 'create'),
			url(r'^(?:(?P<page>\d+)/)?$', news_views.NewsListView.as_view(), name = 'list'),
			url(r'^feeds/latest/$', news_feeds.NewsFeed(), name = 'feed-latest'),
		)
		return (urlpatterns, self.app_name, self.name)

urlpatterns = Patterns().urls
