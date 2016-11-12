from __future__ import unicode_literals
from datetime import date

from django.core.urlresolvers import reverse
from django.core.validators import MaxValueValidator
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from .utils.models import UrlMixin, CreationModificationDateMixin


@python_2_unicode_compatible
class Experiment(CreationModificationDateMixin, UrlMixin):
    name = models.CharField(max_length=255, unique=True)
    template_name = models.CharField(max_length=255, unique=True,
                                     help_text=_("Example : '/main/signup.html'. Original Template"))
    goal = models.CharField(max_length=255, unique=True,
                            help_text=_("Example : '/main/signup_complete'. The path on goal Completion"))
    start = models.DateField(blank=False, db_index=True,
                             help_text=_("This Test starts at UTC +00:00 at the selected Date."))
    end = models.DateField(blank=False, null=True,
                           help_text=_("This Test ends at UTC +00:00 at the selected Date."))
    percentage = models.PositiveIntegerField(_("Traffic Percentage"), validators=[MaxValueValidator(100), ], default=50,
                                             help_text=_("Percentage of traffic to redirect to Variant B"))
    is_active = models.BooleanField(_("Active"), default=False)

    class Meta:
        verbose_name = _("Experiment")
        verbose_name_plural = _("Experiments")

    def __str__(self):
        return self.name

    def get_url_path(self):
        return reverse(
            "experiment_details", kwargs={
                    "experiment_id": str(self.pk)
                }
        )

    def save(self, *args, **kwargs):
        if self.start > date.today() or self.end < date.today():
            self.is_active = False
        super(Experiment, self).save(*args, **kwargs)


@python_2_unicode_compatible
class Test(models.Model):
    experiment = models.ForeignKey(Experiment)
    template_name = models.CharField(max_length=255, unique=True,
                                     help_text=_("Example : '/main/signup1.html'. Template to be Tested"))
    hits = models.IntegerField(blank=True, default=0,
                               help_text=_("# Uniques who have seen this test."))
    conversions = models.IntegerField(blank=True, default=0,
                                      help_text=_("# Uniques that have reached the goal from this test."))

    class Meta:
        verbose_name = _("Test")
        verbose_name_plural = _("Tests")

    def __str__(self):
        return self.template_name
