from __future__ import unicode_literals

from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.core.validators import MaxValueValidator
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _


@python_2_unicode_compatible
class Experiment(models.Model):
    name = models.CharField(max_length=255, unique=True)
    template_name = models.CharField(max_length=255, unique=True,
                                    help_text= ("Example : '/main/signup.html'. Original Template"))
    goal = models.CharField(max_length=255, unique=True,
                                    help_text=_("Example : '/main/signup_complete'. The path on goal Completion"))
    start = models.DateTimeField(blank=False, db_index=True,
                                    help_text=_("This Test starts at the selected Date."))
    end = models.DateTimeField(blank=False, null=True,
                                    help_text=_("This Test ends at the selected Date."))
    percentage = models.PositiveIntegerField(_("Traffic Percentage"), validators=[MaxValueValidator(100), ], default=50,
                                    help_text=_("Percentage of traffic to redirect to Variant B"))
    cancelled = models.BooleanField(_("Cancelled"), default=False)
    created = models.DateTimeField(_("Creation Date and Time"), auto_now_add=True)
    updated = models.DateTimeField(_("Last Update Date and Time"), auto_now=True)

    class Meta:
        verbose_name = _("Experiment")
        verbose_name_plural = _("Experiments")

    def __str__(self):
        return self.name

    def get_experiment_key(self):
        return "ab_exp_key_%s" % self.name

    @property
    def is_active(self):
        return (
            not self.cancelled and
            self.start <= timezone.now() < self.end
        )

    def get_status(self):
        '''
            Returns the Experiment Status based on the Start Date and End Date
        '''
        today = timezone.now()
        if self.start > today or self.end < today:
            active = False
        else:
            active = True
        return active

    def get_updated_traffic(self):
        '''
            Returns the updated network traffic percentage
            for the first Test of the current Experiment
        '''
        test_1, test_2 = self.test_set.all()
        try:
            test_1_ratio = float(test_1.conversions) / test_1.hits
            test_2_ratio = float(test_2.conversions) / test_2.hits
            updated_traffic = int(test_2_ratio*100/(test_1_ratio+test_2_ratio))
            return updated_traffic
        except ZeroDivisionError:
            return 50

    def get_absolute_url(self):
        return reverse(
            "experiment_details", kwargs={
                    "experiment_id": str(self.pk)
                }
        )


@python_2_unicode_compatible
class Test(models.Model):
    experiment = models.ForeignKey(Experiment)
    template_name = models.CharField(max_length=255, unique=True,
                    help_text=_(
                        "Example : '/main/signup1.html'. Template to be Tested"
                            ))
    hits = models.PositiveIntegerField(blank=True, default=0,
                    help_text=_(
                        "# Uniques who have seen this test."
                            ))
    conversions = models.PositiveIntegerField(blank=True, default=0,
                    help_text=_(
                        "# Uniques that have reached the goal from this test."
                            ))

    class Meta:
        verbose_name = _("Test")
        verbose_name_plural = _("Tests")

    def __str__(self):
        return self.template_name

    def save(self, *args, **kwargs):
        tests = Test.objects.filter(experiment=self.experiment).count()
        try:
            current_test = Test.objects.get(id=self.pk)
            super(Test, self).save(*args, **kwargs)
        except:
            pass
            if tests < 2:
                super(Test, self).save(*args, **kwargs)
            else:
                raise ValidationError(
                    "can only create 2 Tests currently for a single Experiment"
                        )
