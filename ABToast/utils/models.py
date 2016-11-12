from __future__ import unicode_literals
import urlparse

from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _


class UrlMixin(models.Model):
    class Meta:
        abstract = True

    def get_url(self):
        if hasattr(self.get_url_path, "dont_recurse"):
            raise NotImplementedError
        try:
            path = self.get_url_path()
        except NotImplementedError:
            raise
        website_url = getattr(
            settings, "DEFAULT_WEBSITE_URL",
            "http://127.0.0.1:8000"
        )
        return website_url + path

    def get_url_path(self):
        if hasattr(self.get_url, "dont_recurse"):
            raise NotImplementedError
        try:
            url = self.get_url()
        except NotImplementedError:
            raise
        bits = urlparse.urlparse(url)
        return urlparse.urlunparse(("", "") + bits[2:])
    get_url_path.dont_recurse = True

    def get_absolute_url(self):
        return self.get_url_path()


class CreationModificationDateMixin(models.Model):
    created = models.DateTimeField(
        _("Creation Date and Time"),
        editable=False,
        auto_now_add=True,
    )
    modified = models.DateTimeField(
        _("Modification Date and Time"),
        null=True,
        editable=False,
        auto_now=True,
    )

    def save(self, *args, **kwargs):
        super(CreationModificationDateMixin, self).save(*args, **kwargs)
    save.alters_data = True

    class Meta:
        abstract = True
