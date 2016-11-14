import random

from .models import Experiment, Test


class AB(object):

    def __init__(self, request):
        self.request = request

    def is_active(self):
        return "active" in self.request.session

    def is_converted(self, exp):
        return self._is_experiment_active(exp)\
         and not self._is_experiment_converted(exp) \
         and exp.goal in self.request.path

    def _is_experiment_active(self, exp):
        return exp.get_experiment_key() in self.request.session

    def _is_experiment_converted(self, exp):
        return "converted" \
         in self.request.session[exp.get_experiment_key()]

    def _get_traffic(self, percentage):
        return 0 if random.random() <= percentage else 1

    def _get_test(self, exp):
        tests = exp.test_set.all()
        test_index = self._get_traffic(exp.percentage / 100.0)
        test = tests[test_index]
        return test

    def run(self, template_name):
        try:
            exp = Experiment.objects.get(template_name=template_name)
        except Experiment.DoesNotExist:
            return template_name

        if not exp.is_active:
            return template_name

        key = exp.get_experiment_key()
        if not self._is_experiment_converted(exp) and self._is_experiment_active(exp):
            return self.request.session[key]["template"]

        test = self._get_test(exp)
        self.activate(test, key)

        return test.template_name

    def activate(self, test, key):
        test.hits += 1
        test.save()
        self.request.session[key] = {
                "id": test.id,
                "template": test.template_name
            }

        self.request.session["active"] = True

    def convert(self, exp):
        key = exp.get_experiment_key()
        test_id = self.request.session[key]["id"]
        test = Test.objects.get(pk=test_id)
        test.conversions += 1
        test.save()
        self.request.session[key]["converted"] = True
        self.request.session.modified = True
