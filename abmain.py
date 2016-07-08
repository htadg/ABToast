import datetime
import random

from django.template import TemplateDoesNotExist
from .models import Experiment, Test


class AB(object):

    def __init__(self, request):
        self.request = request

    def is_active(self):
        return "active" in self.request.session

    def is_converted(self, exp):
        return self.is_experiment_active(exp) and not self.is_experiment_converted(exp) \
                    and exp.goal in self.request.path

    def is_experiment_active(self, exp):
        return self.get_experiment_key(exp) in self.request.session

    def is_experiment_converted(self, exp):
        return "converted" in self.request.session[self.get_experiment_key(exp)]

    def get_traffic(self, percentage):
        return 0 if random.random() < percentage else 1

    def get_test(self, exp):
        tests = exp.test_set.all()
        self.update_traffic(exp)
        test_index = self.get_traffic(exp.percentage / 100)
        test = tests[test_index]
        return test

    def get_experiment_key(self, exp):
        return "ab_exp_key_%s" % exp.name

    def get_experiment(self, template_name):
        return Experiment.objects.get(template_name=template_name)

    def update_traffic(self, exp):
        test_1, test_2 = exp.test_set.all()
        if test_1.hits >=5 and test_2.hits >=5 and test_1.conversions >= 1 and test_2.conversions >=1:
            test_1_ratio = float(test_1.conversions) / test_1.hits
            test_2_ratio = float(test_2.conversions) / test_2.hits
            updated_traffic = int(test_2_ratio * 100/(test_1_ratio + test_2_ratio))
            return updated_traffic
        else:
            return 50

    def run(self, template_name):
        try:
            exp = self.get_experiment(template_name)
        except Experiment.DoesNotExist:
            return template_name
        print exp.template_name

        # start_date = datetime.datetime.strptime(exp.start, "%Y-%m-%d")
        # end_date = datetime.datetime.strptime(exp.end, "%Y-%m-%d")

        start_date = exp.start
        end_date = exp.end

        if start_date > datetime.date.today() or end_date < datetime.date.today():
            if exp.is_active:
                exp.is_active = False
                exp.save()
            return template_name
        if not exp.is_active:
            return template_name

        key = self.get_experiment_key(exp)
        if self.is_experiment_active(exp):
            return self.request.session[key]["template"]

        test = self.get_test(exp)
        self.activate(test, key)

        return test.template_name

    def activate(self, test, key):
        test.hits += 1
        test.save()
        print "==========================="
        print "Hits Updated"
        print "==========================="
        self.request.session[key] = {"id": test.id, "template": test.template_name}

        self.request.session["active"] = True

    def convert(self, exp):
        key = self.get_experiment_key(exp)
        test_id = self.request.session[key]["id"]
        test = Test.objects.get(pk=test_id)
        test.conversions += 1
        test.save()
        print "==========================="
        print "Conversions Updated"
        print "==========================="

        self.request.session[key]["converted"] = True
        self.request.session.modified = True
