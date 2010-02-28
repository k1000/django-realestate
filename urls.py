# -*- coding: UTF-8 -*-
from django.conf.urls.defaults import *
from django.views.generic import list_detail, date_based
#from django.conf import settings
from mysite.estate.models import Property
from mysite.estate.views import search
#import settings

urlpatterns = patterns('',
#  (r'^list/(?P<page>[0-9]+)/$',              'django.views.generic.list_detail.object_list',  properties_list),
    (r'^(?P<object_id>[0-9]+)/$',	 'mysite.estate.views.get_property'),
    (r'^(?P<object_id>[0-9]+)_[a-z\-0-9]+/$',  'mysite.estate.views.get_property'),
    (r'^(type|tipo)/(?P<p_type>[0-9]+)/$',  'mysite.estate.views.list_property_type'),
    #(r'^featured/$', 'django.views.generic.list_detail.object_list', {'queryset':Property.available.featured()}),
    (r'^zone/(?P<p_type>[a-z0-9\-]+)/$',    'mysite.estate.views.list_property_zone'),
    (r'^export_xml/$', 'mysite.estate.views.export_xml'),
    (r'^search/$', 'mysite.estate.views.search'),
    (r'^contact/$', 'mysite.contact_form.contact'),
    (r'$','django.views.generic.list_detail.object_list',  {'queryset':Property.available.all()} ),
)