import json
import os
from zipfile import ZipFile

import requests
from django.contrib.gis.geos import GEOSGeometry, MultiPolygon
from typing import List, Dict

from django.conf import settings
from django.contrib.gis.db.models import MultiPolygonField
from django.contrib.gis.db.models import PointField
from django.contrib.postgres.fields import JSONField
from django.core.cache import cache
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import get_language
from io import BytesIO

from common.cachable import CacheablePropertyMixin, cacheable
from maps.converter import encode_geometry
from maps.fields import ExternalIdField
from maps.infobox import query_by_wikidata_id

ZOOMS = (
    (3, 'world'),
    (4, 'large country'),
    (5, 'big country'),
    (6, 'country'),
    (7, 'small country'),
    (8, 'little country'),
    (9, 'region'),
)


class RegionManager(models.Manager):
    def get_queryset(self):
        return super(RegionManager, self).get_queryset().defer('polygon')


class Region(CacheablePropertyMixin, models.Model):
    title = models.CharField(max_length=128)
    polygon = MultiPolygonField(geography=True)
    parent = models.ForeignKey('Region', null=True, blank=True)
    modified = models.DateTimeField(auto_now=True)
    wikidata_id = ExternalIdField(max_length=20, link='https://www.wikidata.org/wiki/{id}', null=True)
    osm_id = models.PositiveIntegerField(unique=True)
    osm_data = JSONField(default={})
    is_enabled = models.BooleanField(default=True)

    objects = RegionManager()
    caches = {
        'polygon_center': 'region{id}center',
        'polygon_gmap': 'region{id}gmap',
        'polygon_bounds': 'region{id}bounds',
        'polygon_strip': 'region{id}strip',
        'polygon_infobox': 'region{id}infobox',
    }

    class Meta:
        verbose_name = 'Region'
        verbose_name_plural = 'Regions'

    def __str__(self):
        return self.title

    def __init__(self, *args, **kwargs):
        super(Region, self).__init__(*args, **kwargs)

    @property
    @cacheable
    def polygon_bounds(self) -> List:
        return self.polygon.extent

    @property
    @cacheable
    def polygon_strip(self) -> List:
        simplify = self.polygon.simplify(0.01, preserve_topology=True)
        return encode_geometry(simplify, min_points=15)

    @property
    @cacheable
    def polygon_gmap(self) -> List:
        simplify = self.polygon.simplify(0.005, preserve_topology=True)
        return encode_geometry(simplify)

    @property
    @cacheable
    def polygon_center(self) -> List:
        # http://lists.osgeo.org/pipermail/postgis-users/2007-February/014612.html
        return list(self.polygon.centroid)

    def infobox_status(self, lang: str) -> Dict:
        fields = ('name', 'wiki', 'capital', 'coat_of_arms', 'flag')
        trans = self.load_translation(lang)
        result = {field: field in trans.infobox for field in fields}
        result['capital'] = result.get('capital') and isinstance(trans.infobox['capital'], dict)
        return result

    @property
    @cacheable
    def polygon_infobox(self) -> Dict:
        result = {}
        for trans in self.translations.all():
            infobox = trans.infobox
            infobox.pop('geonamesID', None)
            if 'capital' in infobox and isinstance(infobox['capital'], dict):
                del (infobox['capital']['id'])
            result[trans.language_code] = infobox
        return result

    def full_info(self, lang: str) -> Dict:
        return {'infobox': self.polygon_infobox[lang], 'polygon': self.polygon_gmap, 'id': self.id}

    def update_polygon(self) -> None:
        def content():
            cache = os.path.join(settings.GEOJSON_DIR, '{}.geojson'.format(self.osm_id))
            if not os.path.exists(cache):
                url = settings.OSM_URL.format(id=self.osm_id, key=settings.OSM_KEY, level=2 if self.country.is_global else 4)
                response = requests.get(url)
                if response.status_code != 200:
                    raise Exception('Bad request')
                zipfile = ZipFile(BytesIO(response.content))
                zip_names = zipfile.namelist()
                if len(zip_names) != 1:
                    raise Exception('Too many geometries')
                filename = zip_names.pop()
                with open(cache, 'wb') as c:
                    c.write(zipfile.open(filename).read())
            with open(cache, 'r') as c:
                return json.loads(c.read())

        geojson = content()
        self.polygon = GEOSGeometry(json.dumps(geojson['features'][0]['geometry']))
        simplify = self.polygon.simplify(0.01, preserve_topology=True)
        if not isinstance(simplify, MultiPolygon):
            simplify = MultiPolygon(simplify)
        self.polygon = simplify
        self.save()

    @property
    def translation(self):
        return self.load_translation(get_language())

    def load_translation(self, lang):
        return self.translations.filter(language_code=lang).first()

    def update_infobox(self) -> None:
        wikidata_id = None if self.parent is None else self.parent.wikidata_id
        rows = query_by_wikidata_id(country_id=wikidata_id, item_id=self.wikidata_id)
        for lang, infobox in rows.items():
            trans = self.load_translation(lang)
            trans.master = self
            trans.infobox = infobox
            trans.name = infobox.get('name', '')
            trans.save()


class RegionTranslation(models.Model):
    name = models.CharField(max_length=120)
    infobox = JSONField(default={})
    language_code = models.CharField(max_length=15, db_index=True)
    master = models.ForeignKey(Region, related_name='translations', editable=False)

    class Meta:
        unique_together = ('language_code', 'master')
        db_table = 'maps_region_translation'


@receiver(post_save, sender=Region, dispatch_uid="clear_region_cache")
def clear_region_cache(sender, instance: Region, **kwargs):
    for key in instance.caches:
        cache.delete(instance.caches[key].format(id=instance.id))


class Game(models.Model):
    image = models.ImageField(upload_to='upload/puzzles', blank=True, null=True)
    slug = models.CharField(max_length=15, db_index=True)
    center = PointField(geography=True)
    zoom = models.PositiveSmallIntegerField(choices=ZOOMS)
    is_published = models.BooleanField(default=False)
    is_global = models.BooleanField(default=False)
    regions = models.ManyToManyField(Region)

    class Meta:
        abstract = True

    def __str__(self) -> str:
        return self.slug

    def get_absolute_url(self) -> str:
        raise NotImplementedError

    def load_translation(self, lang):
        return self.translations.filter(language_code=lang).first()

    @property
    def index(self) -> Dict:
        trans = self.load_translation(get_language())
        return {'image': self.image, 'slug': self.slug, 'name': trans.name}

    def get_init_params(self) -> Dict:
        return {
            'zoom': self.zoom,
            'center': {'lng': self.center.coords[0], 'lat': self.center.coords[1]}
        }


class GameTranslation(models.Model):
    name = models.CharField(max_length=15)
    language_code = models.CharField(max_length=15, db_index=True)
    master = models.ForeignKey(Game, related_name='translations', editable=False)

    class Meta:
        unique_together = ('language_code', 'master')
        abstract = True
