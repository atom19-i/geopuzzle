from django.contrib.sitemaps import Sitemap
from django.core.urlresolvers import reverse
from django.utils import timezone

from maps.models import Country


class RegionSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.5

    def items(self):
        return Country.objects.filter(is_published=True)

    def lastmod(self, country):
        return timezone.now()


class PuzzleSitemap(RegionSitemap):
    def location(self, country):
        return reverse('puzzle_map', kwargs={'name': country.slug})


class QuizSitemap(RegionSitemap):
    def location(self, country):
        return reverse('quiz_map', kwargs={'name': country.slug})


class WorldSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.8

    def items(self):
        return 'index', 'world'

    def location(self, object):
        if object == 'index':
            return reverse(object)
        country = Country.objects.get(slug=object)
        return country.get_absolute_url()