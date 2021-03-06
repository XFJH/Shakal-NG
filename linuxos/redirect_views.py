# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.http import HttpResponsePermanentRedirect
from article.models import Article
from news.models import News
from polls.models import Poll
from wiki.models import Page as WikiPage

def profile_redirect(request, pk):
	return HttpResponsePermanentRedirect(reverse('auth_profile', kwargs = {'pk': pk}))

def article_redirect(request, pk):
	article = get_object_or_404(Article, pk = pk)
	return HttpResponsePermanentRedirect(reverse('article:detail-by-slug', kwargs = {'slug': article.slug}))

def forum_topic_redirect(request, pk):
	return HttpResponsePermanentRedirect(reverse('forum:topic-detail', kwargs = {'pk': pk}))

def forum_topic_old_redirect(request):
	return HttpResponsePermanentRedirect(reverse('forum:topic-detail', kwargs = {'pk': request.GET['forumid']}))

def news_redirect(request, pk):
	news = get_object_or_404(News, pk = pk)
	return HttpResponsePermanentRedirect(reverse('news:detail-by-slug', kwargs = {'slug': news.slug}))

def poll_redirect(request, pk):
	poll = get_object_or_404(Poll, pk = pk)
	return HttpResponsePermanentRedirect(reverse('polls:detail-by-slug', kwargs = {'slug': poll.slug}))

def wiki_redirect(request, pk):
	wiki = get_object_or_404(WikiPage, pk = int(pk) + 7)
	return HttpResponsePermanentRedirect(reverse('wiki:page', kwargs = {'slug': wiki.slug}))
def forum_rss_redirect(request):
	return HttpResponsePermanentRedirect(reverse('forum:feed-latest'))
def news_rss_redirect(request):
	return HttpResponsePermanentRedirect(reverse('news:feed-latest'))
def article_rss_redirect(request):
	return HttpResponsePermanentRedirect(reverse('article:feed-latest'))
