# -*- coding: utf-8 -*-
import os

from django import template
from django_tools.middlewares.ThreadLocal import get_current_request


def process_template_args(rawparams, context = None):
	args = []
	for param in rawparams:
		pos = param.find('=')
		if (pos > 0):
			break
		if context is not None:
			param = template.resolve_variable(param, context)
		args.append(param)
	return args


def process_template_kwargs(rawparams, context = None):
	kwargs = {}
	for param in rawparams:
		paramname = param
		paramvalue = ''
		pos = param.find('=')
		if (pos <= 0):
			continue
		paramname = param[:pos]
		paramvalue = param[pos + 1:]
		if context is not None:
			paramvalue = template.resolve_variable(paramvalue, context)
		kwargs[paramname] = paramvalue
	return kwargs


def iterify(items):
	try:
		iter(items)
		return items
	except:
		return [items]


def build_absolute_uri(path):
	request = get_current_request()
	if request:
		return request.build_absolute_uri(path)
	else:
		from django.conf import settings
		from django.contrib.sites.models import Site
		return 'http://' + Site.objects.get(pk = settings.SITE_ID) + path


def clean_dir(path, root_path):
	path = os.path.abspath(path)
	root_path = os.path.abspath(root_path)

	current_dir = path
	while len(os.path.split(current_dir)) and current_dir.startswith(root_path) and current_dir != root_path:
		try:
			os.rmdir(current_dir)
		except OSError:
			return
		current_dir = os.path.join(*os.path.split(current_dir)[:-1])
