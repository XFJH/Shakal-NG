# -*- coding: utf-8 -*-
from django import template
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.safestring import mark_safe

from common_utils import iterify
from threaded_comments.models import Comment, RootHeader, UserDiscussionAttribute


register = template.Library()


class DiscussionLoader:
	def get_target_ctype_pk(self):
		return ContentType.objects.get_for_model(self.target), self.target.pk

	def get_comments_query_set(self):
		ctype, object_id = self.get_target_ctype_pk()
		if not object_id:
			return Comment.objects.none()

		queryset = Comment.objects.filter(
			content_type = ctype,
			object_id = object_id,
		)
		queryset = queryset.select_related('user__profile', 'user__rating', )
		queryset = queryset.prefetch_related('attachments')
		queryset = queryset.order_by('lft')
		return queryset

	def get_root_node(self):
		if self.root_node is None:
			ctype, object_id = self.get_target_ctype_pk()
			self.root_node, created = Comment.objects.get_root_comment(ctype, object_id)
		return self.root_node

	def get_query_set(self):
		ctype, object_id = self.get_target_ctype_pk()
		queryset = self.get_comments_query_set()
		if not queryset.has_root_item():
			Comment.objects.get_root_comment(ctype, object_id)
			queryset = self.get_comments_query_set()
		return queryset

	def get_discussion_attribute(self):
		ctype, object_id = self.get_target_ctype_pk()
		header = RootHeader.objects.get(content_type = ctype, object_id = object_id)
		(discussion_attribute, created) = UserDiscussionAttribute.objects.get_or_create(user = self.context['user'], discussion = header)
		return discussion_attribute

	def highlight_new(self, query_set):
		root_item = query_set.get_root_item()
		prev_new_item = root_item
		for comment in query_set:
			if comment.is_new:
				prev_new_item.next_new = comment.pk
				if prev_new_item != root_item:
					comment.prev_new = prev_new_item.pk
				prev_new_item = comment

	def update_discussion_attribute(self, discussion_attribute):
		discussion_attribute.time = timezone.now()
		discussion_attribute.save()

	def get_last_display_time(self, discussion_attribute):
		last_display_time = timezone.now()
		if discussion_attribute.time:
			last_display_time = discussion_attribute.time
		return last_display_time

	def load(self, context, target):
		self.target = target
		self.context = context
		attrib = None
		query_set = self.get_query_set()
		if 'user' in context and context['user'].is_authenticated():
			attrib = self.get_discussion_attribute()
			last_display_time = self.get_last_display_time(attrib)
			self.update_discussion_attribute(attrib)
			query_set = query_set.extra(select = {'is_new': 'submit_date >= %s'}, select_params = (last_display_time, ))[:]
			self.highlight_new(query_set)
		setattr(query_set, 'root_header', query_set.get_root_item().root_header())
		if 'user' in context and context['user'].is_authenticated():
			setattr(query_set, 'user_attribute', attrib)
		return query_set


@register.assignment_tag(takes_context = True)
def get_threaded_comments_list(context, target):
	loader = DiscussionLoader()
	return loader.load(context, target)


@register.simple_tag(takes_context = True)
def render_threaded_comments_toplevel(context, target):
	model_class = target.__class__
	templates = [
		"comments/{0}_{1}_comments_toplevel.html".format(*str(model_class._meta).split('.')),
		"comments/{0}_comments_toplevel.html".format(model_class._meta.app_label),
		"comments/comments_toplevel.html".format(model_class._meta.app_label),
	]
	context.update({"target": target})
	return mark_safe(render_to_string(templates, context))


@register.simple_tag(takes_context = True)
def add_discussion_attributes(context, model):
	model = iterify(model)
	if len(model) == 0:
		return ''

	content_type = ContentType.objects.get_for_model(model[0].__class__)
	id_list = [m.id for m in model]

	headers = RootHeader.objects \
		.filter(content_type = content_type, object_id__in = id_list) \
		.values('id', 'object_id', 'last_comment', 'comment_count', 'is_locked')

	if 'user' in context and context['user'].is_authenticated():
		header_ids = [h['id'] for h in headers]
		user_attributes = UserDiscussionAttribute.objects \
			.filter(user = context['user'], discussion__in = header_ids) \
			.values('discussion_id', 'time', 'watch')
		user_attributes = dict([(a['discussion_id'], a) for a in user_attributes])
		for header in headers:
			header.update(user_attributes.get(header['id'], {}))
	headers = dict([(h['object_id'], h) for h in headers])

	for obj in model:
		hdr = headers.get(obj.pk, {})
		obj.last_comment = hdr.get('last_comment', None)
		obj.comment_count = hdr.get('comment_count', 0)
		obj.is_locked = hdr.get('is_locked', False)
		obj.rootheader_id = hdr.get('id', None)
		obj.discussion_display_time = hdr.get('time', None)
		obj.discussion_watch = hdr.get('watch', None)
		if obj.last_comment and obj.discussion_display_time:
			obj.new_comments = obj.discussion_display_time < obj.last_comment
		else:
			obj.new_comments = None
	return ''


@register.inclusion_tag("comments/comment_count.html")
def get_comments_for_item(item, display_last = False):
	return {'item': item, display_last: 'display_last'}


@register.simple_tag
def comment_form_target():
	return reverse("comments-post-comment")
