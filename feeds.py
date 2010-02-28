# -*- coding: UTF-8 -*-
from django.conf import settings
from django.contrib.syndication.feeds import Feed
from django.utils.translation import ugettext as _

from mysite.estate.models import Property

class LatestProperties(Feed):
    title = _("propiedades recien anadidas en www.eliterealestate.eu)")
    link = settings.SITE
    description = _("visita ")
    def items(self):
        return Property.available.all()[:10]

class FeaturedProperties(Feed):
    title = _("propiedades destacadas en www.eliterealestate.eu)")
    link = settings.SITE
    description = _("Updates on changes and additions to chicagocrime.org.")
    def items(self):
        return Property.available.filter(is_featured__exact = True)[:10]
        
class SimilarProperties(Feed):
    title = _("TODOpropiedades destacadas en www.eliterealestate.eu)")
    link = settings.SITE
    description = _("Updates on changes and additions to chicagocrime.org.")
    def items(self):
        return Property.available.filter(is_featured__exact = True)[:10]
