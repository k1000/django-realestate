# -*- coding: UTF-8 -*-
import urllib
from django.views.generic.list_detail import object_list, object_detail
from django.contrib.syndication.views import feed
from django import forms as forms
from django.forms import widgets#from django import forms
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.utils.translation import ugettext_lazy as _

from mysite.estate.models import *
from mysite.zona.models import Zona as zone
from django.conf import settings
'''
.extra(select={'total_votes':"SELECT `type`, COUNT (`type`) as total FROM `estate_property` GROUP by `type` ORDER by `type` DESC"},)
'''

def front_page(request):
    return object_list(request, 
                        queryset=Property.featured.all(),
                        template_name='estate/front_page.html',
                        )

def list_property_type(request, p_type):
    return object_list(request, 
                        queryset=Property.available.filter(type__exact=p_type), 
                        #template_name='estate/properties_list.html', 
                        paginate_by=5,
                        allow_empty=True,
                        )

def export_xml(request):
    return object_list(request, 
                        queryset=Property.available.all(),
                        mimetype='xml',
                        template_name = 'estate/property_export.xml',
                        extra_context={ 'site':'mypropertysite' },
                        allow_empty=True,)

def export_xml_trovit(request):
    return object_list(request, 
                        queryset=Property.available.all(),
                        mimetype='xml',
                        template_name = 'estate/export_trovit.xml',
                        allow_empty=True,)
                        
def list_properties_in_zone(request, p_zone):
    zones_index = [str(p_zone)]+[ '%s' % z.id for z in list(Zone.objects.get(id = p_zone).get_all_children())]
    return object_list(request, 
                        #queryset=Property.available.filter(zone__exact=p_type), 
                        queryset=Property.available.extra(where=['zone_id IN (%s)' % ', '.join(zones_index)]),
                        paginate_by=5,
                        allow_empty=True,
                        )
                        
def get_property(request, object_id):
    gallery = Image.objects.select_related().filter(gallery__property = object_id)
    return object_detail(request,
                       queryset= Property.objects.all(),
                       object_id = object_id,
                       extra_context={'gallery': gallery, 'google_key': settings.GOOGLE_MAPS_KEY})

class SearchForm(forms.Form):
    type = forms.ChoiceField(label = _('busca'),choices=  [('',_('Propiedad'))]+[(x, y ) for x, y in Property.TYPE], required=False )
    status = forms.ChoiceField(label = _('en régimen'), choices= [('V', _('en venta')), ('A', _('en alquiler')), ])
    price = forms.ChoiceField(label = _('hasta'),
            choices = (('',_('sin limite de precio')), ('80000', '80.000€'), ('100000', '100.000€'), ('120000', '120.000€'), ('140000', '140.000€'), ('160000', '160.000€'), ('180000', '180.000€'), ('200000', '200.000€'), ('240000', '240.000€'), ('300000', '300.000€'), ('400000', '400.000€'), ('500000', '500.000€'), ('600000', '600.000€')),  required=False)
    zone_id = forms.ChoiceField(label = _('en zona'), choices=[('',_('cualquiera'))] + [(o.id, o) for o in Zone.objects.all()], required=False )
    bedrooms = forms.ChoiceField(label = _('con dormitorios'), choices=[('',_('sin precisar'))] + [(o, o) for o in range(1,8)], required=False )
    #bathrooms = forms.ChoiceField(label = _('baños'), choices=[('','-')] + [(o, o) for o in range(1,4)], required=False )
    features = forms.MultipleChoiceField(label = _('tiene'),  choices=[(o.id, o) for o in Features.objects.all()], required=False)

def search(request):
    search_form = None
    
    if request.method == 'GET':
        try:
            current_page = int(request.GET.get('page', '1'))
        except ValueError:
            current_page = 1
            
        search_form = SearchForm(request.GET)
        if search_form.is_valid():
            new_data = request.GET.copy()
            fields = []
            values = []
            for e in search_form.fields:
                if e not in new_data:
                    break
                if e == 'features':
                    break
                elif (e == 'price') & (new_data[e] != ''):
                    fields.append(e + '<%s')
                    values.append(new_data[e])
                elif new_data[e] != '' :
                    fields.append(e + '=%s')
                    values.append(new_data[e])
            prop_lists = Property.available.extra(where=fields, params=values)
            # get belonging zones
            if 'zone_id' in new_data:
                if new_data['zone_id']:
                    zones_index = [new_data['zone_id']]+[ '%s' % z.id for z in list(Zone.objects.get(id = new_data['zone_id']).get_all_children())]
                    # search belonging zones
                    if len(zones_index) > 0:
                        prop_lists = Property.available.extra(where=['zone_id IN (%s)' % ', '.join(zones_index)])
            
            #paginator = Paginator(prop_lists, 5)
            #try:
                #props = paginator.page(current_page)
            #except (EmptyPage, InvalidPage):
                #props = paginator.page(paginator.num_pages)
          
            if 'page' in new_data:
                del new_data['page']
            return object_list(request,
                    queryset=prop_lists,
                    allow_empty=True,
                    paginate_by = 5,
                    template_name='estate/property_list.html',
                    extra_context={ 'search_form': search_form, 'get_query':urllib.urlencode(new_data) }
                    )

def build_search_form(request):
    return {'search_form': SearchForm(),}

