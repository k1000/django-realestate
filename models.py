# -*- coding: utf-8 -*-
import datetime
#
from django.db import models
from django.utils.translation import get_language
from django.dispatch import dispatcher
from django.db.models import signals
from django.utils.translation import ugettext
from django.utils.translation import ugettext_lazy as _
#
from mysite.thumbnail.field import ImageWithThumbnailField
from mysite.zona.models import Zona as Zone
from mysite.utils.text import trans
from mysite.estate.signals import *
#
from mysite.localization.localization import format

PROVINCIA = (
    ('Las Palmas', 'Las Palmas'),
    ('Santa Cruz de Tenerife', 'S/C de Tenerife'),
    ('Galicia', 'Galicia'),
)
STREAT = (
    ('Calle', 'Calle'),
    ('Plaza', 'Plaza'),
    ('Avenida', 'Avenida'),
    ('Camino', 'Camino'),
    ('Carretera', 'Carretera'),
    ('Via', 'Vìa'),
)
GENDER = (
    ('SR', _('SR')),
    ('SNR', _('SNR')),
)

IMGTIPOS = (
    ('F', _('Foto')),
    ('IMG', _('Imagen')),
    ('PL', _('Plano')),
    ('D', _('Dibujo')),
    ('VR', _('Panorama 360')),
    ('V', _('Representacion virtual')),
)

class Features(models.Model):
   name = models.CharField(max_length=100)

   def __unicode__ (self):
        return trans(self.name)

   class Admin:
        pass

   class Meta:
       verbose_name = _('characteristica')
       verbose_name_plural = _('characteristicas')

class Vendor(models.Model):
   name = models.CharField( _('nombre'), max_length=30)
   surmame  = models.CharField( _('apellidos'), max_length=30)
   gender = models.CharField( _('titulo'), max_length=3, choices=GENDER)
   adresss = models.CharField( _('dirrecion'), max_length=30)
   city = models.CharField( _('ciudad'), max_length=30)
   tel = models.CharField( _('tel.'), max_length=30)
   email = models.EmailField( blank = True)
   comments = models.TextField( _('comentarios'), blank = True)
   nif = models.CharField( _('NIF'), max_length=16, blank = True)

   def __unicode__ (self):
        return self.gender + '. ' + self.name+' '+self.surmame

   class Admin:
        pass

   class Meta:
        verbose_name = _('vendedor')
        verbose_name_plural = _('vendedores')

class AvailableProperty(models.Manager):

    def get_query_set(self):
        return super(AvailableProperty, self).get_query_set().filter(is_published__exact=True, status__exact='V').order_by('-id')

    def featured(self):
        return self.get_query_set().filter(is_featured__exact=True )

    def count_property_types(self):
        from django.db import connection
        cursor = connection.cursor()
        r = cursor.execute("SELECT `type`, `status`, COUNT( `type` ) AS `total` FROM `estate_property` GROUP BY `type` ORDER BY `total` DESC")
        return cursor.fetchall()

class FeaturedProperty(models.Manager):
    def get_query_set(self):
        return super(AvailableProperty, self).get_query_set().filter(is_published__exact=True, status__exact='V', is_featured__exact=True).order_by('-id')


class Property(models.Model):
    objects = models.Manager()
    available = AvailableProperty()
    featured = FeaturedProperty()

    STATUS = (
        ('V', _('en venta')),
        ('F', _('vendido')),
        ('S', _('en "stand-by"')),
        ('R', _('reservado')),
        ('A', _('en alquiler')),
        ('B', _('alquilado')),
    )
    TYPE = (
        ('1', _('Terreno Rustico')),
        ('2', _('Terreno Urbano')),
        ('3', _('Estudio')),
        ('4', _('Piso')),
        ('5', _('Casa Adosada')),
        ('6', _('Semi-adosado')),
        ('7', _('Habitacion')),
        ('8', _('Locales')),
        ('9', _('Apartamento')),
        ('10', _('Atico')),
        ('11', _('Caserio'))
    )
    CONDITION = (
        ('1', _('por construir')),
        ('2', _('en construcion')),
        ('3', _('estreno')),
        ('4', _('nuevo')),
        ('5', _('en buen estado')),
        ('6', _('seminuevo')),
        ('7', _('reformado')),
        ('8', _('por reformar')),
        ('9', _('en ruina')),
    )
    SITUATION = (
        ('1', _('Central')),
        ('2', _('Afueras')),
        ('3', _('Campo')),
    )
    APARC = (
        ('0', _('No')),
        ('1', _('Aparcamiento')),
        ('2', _('Garaje')),
    )
    VIEWS = (
        ('0', _('No')),
        ('1', _('Mar')),
        ('2', _('Montana')),
    )
    POOL = (
        ('0', _('No')),
        ('1', _('Comunitaria')),
        ('2', _('Privada')),
    )
    ZONE_TYPE = (
        ('1', _('Costa')),
        ('2', _('Medio')),
        ('3', _('Monte')),
    )
    price = models.PositiveIntegerField( _('precio'),blank = True, null=True)
    vendor = models.ForeignKey(Vendor, verbose_name= _('vendedor'))
    type = models.PositiveSmallIntegerField( _('tipo de propiedad'),max_length=1, choices=TYPE, )
    status = models.CharField( _('situacion'),max_length=1, choices=STATUS, )
    condition = models.PositiveSmallIntegerField( _('estado'),max_length=2, choices=CONDITION, blank = True)
    is_featured = models.BooleanField( _('Destacar?'), default = False,)

    streat_type = models.CharField( _('tipo de via'), max_length=10, choices=STREAT, default='C/.')
    streat = models.CharField( _('calle'), max_length=255)
    street_nr = models.PositiveIntegerField( _('nr casa'), max_length=5)
    apartment_nr = models.CharField( _('nr vivienda'), max_length=8, blank = True)
    door = models.CharField( _('puerta'), max_length=8, blank = True)
    postal_code = models.PositiveIntegerField(_('codigo postal'))
    province = models.CharField( _('provincia'), max_length=40, choices=PROVINCIA, default='S/C de Tenerife')
    zone = models.ForeignKey(Zone, verbose_name='zona')
    city = models.CharField(_('ciudad'), max_length=40, help_text=_("nombre completo como 'San Cristobal de La Laguna'"))
    county = models.CharField( _('municipio'), max_length=60, blank = True)
    lat = models.CharField( _('latitud geografica'), max_length=30, blank = True)
    lan = models.CharField( _('longitud geografica'),max_length=30, blank = True)
    situation = models.PositiveSmallIntegerField( _('ubicacion'),choices=SITUATION, default=1)
    zone_type = models.PositiveSmallIntegerField( _('anillo'),choices=ZONE_TYPE, default=1)
    is_location_public = models.BooleanField( _('Publicar la dirrecion?'), default = True)

    created_at = models.DateField( _('introducido en'), editable=False, default= datetime.datetime.now())
    updated_on = models.DateField( _('modificado en'), blank = True, null=True,  editable=False)
    published_by = models.CharField(max_length=30, blank = True, editable=False)
    is_published = models.BooleanField( _('Publicar?'), default = True)
    #published_by = models.ForeignKey(User)

    sqr_meters = models.PositiveIntegerField( _('m<sup>2</sup>'), blank = True, default=0)
    sqr_meters_plot = models.PositiveIntegerField( _('m<sup>2</sup> del terreno'), blank = True, null=True)
    bedrooms = models.PositiveSmallIntegerField( _('dormitorios'), blank = True, null=True)
    bathrooms = models.PositiveSmallIntegerField( _('banos'), blank = True, null=True)
    parking = models.PositiveSmallIntegerField( _('aparcamiento'), choices=APARC,default=1 )
    garage_places = models.PositiveSmallIntegerField( _('plazas de garaje'), blank = True, null=True)
    build_in_year = models.PositiveIntegerField( _('construido en'), blank = True, null= True )
    pool = models.PositiveIntegerField( _('piscina'), choices=POOL, blank = True, default=0)
    views = models.PositiveSmallIntegerField( _('vistas'), choices=VIEWS, default = 0)
    description = models.TextField( _('descripcion'), blank = True, help_text= _('se puede aplicar traducion como "[en]...english text...[/en] texto sin traducir [es]...texto espanol...[/es]" etc'))
    comments = models.TextField( _('comentarios'), help_text= _('!no se van a publicar!'), blank = True)

    default_image = ImageWithThumbnailField( _('imagen de portada'), upload_to = 'uploads', blank = True)

    features = models.ManyToManyField(Features, blank = True)

    def title (self):
        return _(u'%(type)s %(condition)s en %(city)s %(status)s por %(price).0f€') % {'type': self.get_type_display(), 'status': self.get_status_display(), 'condition':self.get_condition_display(), 'city': self.city, 'price': self.price}

    title.short_description = _('titulo')

    def address(self):
        if self.street_nr <> None:
            street_nr = self.street_nr
        else:
            street_nr = ''
        if self.apartment_nr:
            apartment_nr = 'viv. %s' % self.apartment_nr
        else:
            apartment_nr = ''
        if self.door:
            door = 'puerta %s' % self.door
        else:
            door = ''
        return u'%s %s %s %s %s' % ( self.streat_type, self.streat, self.street_nr, apartment_nr, door )

    address.short_description =  _('dirrecion')

    def new_developement(self):
        if self.condition in [ 0, 1, 2]:
            return True
        else:
            return False

    new_developement.short_description = _('nueva promocion?')

    class Meta:
        verbose_name = _('propiedad')
        verbose_name_plural = _('propiedades')

    def __unicode__ (self):
        return 'ID:'+ str(self.id)
        #return Ref.:%s,  %s, %s % (self.zone_id, self.name, self.type_id)

    def save(self):
        if not self.id:
            self.updated_at = datetime.datetime.now()
        super(Property, self).save()


    def get_absolute_url(self):
        return u'/properties/%d_%s/' % (self.id, self.title())

    class Admin:
        list_display = ('title', 'id','address', 'type', 'zone', 'bathrooms', 'bedrooms', 'sqr_meters', 'price', 'status', 'is_published', 'is_featured',)
        list_filter = ('status', 'type', 'zone', 'is_published' )
        search_fields = ('type', 'zone',)
        list_per_page = 50
        save_as = True
        fields = (
            (None, {'fields': (('price', 'vendor'), ('type', 'status'), ('is_published', 'is_featured'), 'condition', 'comments',  )}),
            (_('caracteristicas'), {'fields': (('sqr_meters', 'sqr_meters_plot'), ('bedrooms', 'bathrooms', 'pool'), ('views', 'parking', 'garage_places'), 'build_in_year', 'features', 'description', 'default_image', )}),
            (_('localidad'), {'fields': (('streat_type', 'streat', 'street_nr'), ('apartment_nr', 'door'), ('postal_code', 'city', 'county'), ('province', 'zone' ), ( 'situation', 'zone_type'), ( 'lat', 'lan' ), ('is_location_public'), )}),
        )

#signals
#dispatcher.connect(count_property_types, signal=signals.post_save, sender=Property)
#dispatcher.connect(count_property_types, signal=signals.post_delete, sender=Property)

#dispatcher.connect(send_property_created_email, signal=signals.post_save, sender=Property)

#dispatcher.connect(send_property_to_tenerpiso, signal=signals.post_save, sender=Property)
#dispatcher.connect(delete_property_from_tenerpiso, signal=signals.post_delete, sender=Property)

class Gallery(models.Model):
    property = models.ForeignKey(Property, related_name = ugettext('Propiedad') )
    title = models.CharField(_('titulo'), max_length=255, )
    slug = models.SlugField(_('slug'))
    description = models.TextField( _('descripcion'), blank = True, help_text=_(u'se puede aplicar  traducion como "[en]...english text...[/en] texto sin traducir [es]...texto espanol...[/es]" etc'))
    galery_type = models.CharField( _('tipo'),max_length=3, choices=IMGTIPOS, default='F')

    def __unicode__ (self):
        return str(self.property)+' '+self.title

    class Admin:
        list_display = ('id','title')

    class Meta:
        verbose_name = _('Galeria')
        verbose_name_plural = _('Galerias')


class Image(models.Model):
    gallery = models.ForeignKey(Gallery )
    name = models.CharField( _('descripcion'), max_length=255 )
    image = ImageWithThumbnailField( _('imagen'), upload_to = 'uploads')
    is_published = models.BooleanField( _('Publicar?'), default = True)
    img_type = models.CharField( _('tipo'),max_length=3, choices=IMGTIPOS,)

    def __unicode__ (self):
        return str(self.gallery)+' '+self.name

    class Admin:
        list_display = ('id', 'gallery')

    class Meta:
        verbose_name = _('Imagen')
        verbose_name_plural = _('Imagenes')

#signals
#dispatcher.connect(send_image_to_tenerpiso, signal=signals.post_save, sender=Image)
#dispatcher.connect(delete_image_from_tenerpiso,signal=signals.post_delete, sender=Image)


