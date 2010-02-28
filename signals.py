import urllib
#
from django.core.mail import send_mass_mail
from django.template import Context, loader
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE, DELETION
from django.conf import settings

from mysite.estate.models import *


P_KEY = 'PROPERIES_COUNT_TYPES'

def logger( msg ):
    import logging
    
    logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    filename= settings.TENERPISO_LOG,
                    filemode='w')
    logging.info('get url: %s ' % msg)
    
def count_property_types(sender, instance, signal, *args, **kwargs):
    from django.core.cache import cache
    
    lst = Property.available.count_property_types()
    cache.set(P_KEY, lst, 60 * 60 * 60 * 24 * 365) # cache 1yr
    
def tenerpiso_call(script, param):
    url = '%s/%s' % (settings.TENERPISO_URL, script)
    #auth = 'USUARIO=%s&PASSWORD=%s' % (settings.TENERPISO_USER, settings.TENERPISO_PASS)
    #p = '&'.join([ '%s=%s' % (f, v) for f, v in param])
    auth = [('USUARIO', settings.TENERPISO_USER), ('PASSWORD', settings.TENERPISO_PASS)]
    params = urllib.urlencode(auth + [(key, val.encode('ascii', 'ignore') ) for key, val in param] )
    #print( url + '?' + auth + '&' + p )
    #return urllib.urlopen(url + '?' + auth + '&' + p)
    send = urllib.urlopen(url, params )
    
    if send:
        logger( send )
    else:
        logger( "Can not get url")

def send_property_created_email(sender, instance, signal, *args, **kwargs):
    """
    Sends an email out to a number of people informing them
    of a new blog entry.
    """
    def get_recipient_list():
        # Get a list of the email addresses the message
        # should be sent to.
        recipient_list = ['kamil@zona-e.com'] # Left for you to implement.
        return recipient_list

    try:
        Property.objects.get(id=instance._get_pk_val())
    except (Property.DoesNotExist, AssertionError):
        #The attempt to ge    import loggingt a post with the same id as our
        #instance failed ? a good indication that this is a new post.
        t = loader.get_template('property/new_property_email.txt')
        c = Context({
            'object': instance,
        })
        message = t.render(c)

        subject = 'Nueva Propiedad ha sido introducida'
        from_email = 'kamil@zona-e.com'
        recipient_list = get_recipient_list()

        email = (subject, message, from_email, recipient_list)
        send_mass_mail(email)

def send_property_to_tenerpiso(sender, instance, signal, *args, **kwargs):
    """
    Sends propery details to www.tenerpiso.com
    """
    exit = tenerpiso_call('XMLsavePropiedadExt_20.php',
        [('IDExt', instance.id),
        ('tipo', instance.type),
        ('anillo', instance.zone_type),
        ('situada', instance.situation),
        ('metrosint', instance.sqr_meters),
        ('metrosex', instance.sqr_meters_plot),
        ('rooms', instance.bedrooms),
        ('wc', instance.bathrooms),
        ('aparc', instance.parking),
        ('piscina', instance.pool),
        ('vista', instance.views),
        ('precio', instance.price),
        ('cp', instance.postal_code),
        ('direccion', instance.address()),
        ('regimen', 0),
        ])

            
def delete_property_from_tenerpiso(sender, instance, signal, *args, **kwargs):
    tenerpiso_call('XMLdelPropiedadExt_20.php',[('IDExt', u'%s' % (instance.id))])
    
def send_image_to_tenerpiso(sender, instance, signal, *args, **kwargs):
    """
    Sends image details to www.tenerpiso.com
    """
    from mysite.thumbnail.utils import make_thumbnail
    
    try:
        Image.objects.get(id=instance._get_pk_val())
    except (Image.DoesNotExist, AssertionError):
        tenerpiso_call('XMLaddFotoExt.php',
            [('IDPropEx', instance.gallery.property.id),
            ('IDExt', instance.id),
            ('filename', make_thumbnail(instance.get_image_url(), 500)),
            ('filenameTh', make_thumbnail(instance.get_image_url(), 100)),
            ('text', instance.name)]
        )

def delete_image_from_tenerpiso(sender, instance, signal, *args, **kwargs):
    tenerpiso_call('XMLdelFotoExt.php',[('IDExt', instance.id)])