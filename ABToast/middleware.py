from datetime import date
from threading import local

from django.utils.deprecation import MiddlewareMixin

from .abmain import AB
from .models import Experiment


_thread_locals = local()


def get_current_request():
    return getattr(_thread_locals, 'request', None)


def get_updated_traffic(exp):
    test_1, test_2 = exp.test_set.all()
    try:
        test_1_ratio = float(test_1.conversions) / test_1.hits
        test_2_ratio = float(test_2.conversions) / test_2.hits
        updated_traffic = int(test_2_ratio * 100/(test_1_ratio + test_2_ratio))
        return updated_traffic
    except ZeroDivisionError:
        return 50


def get_status(exp):
    start = exp.start
    end = exp.end
    if start > date.today() or end < date.today():
        active = False
    else:
        active = True
    return active


class ABMiddleware(MiddlewareMixin):
    def process_request(self, request):
        _thread_locals.request = request
        request.ab = AB(request)
        if request.ab.is_active():
            exps = Experiment.objects.all()
            for exp in exps:
                exp.is_active = get_status(exp)
                if exp.is_active:
                    exp.percentage = get_updated_traffic(exp)
                exp.save()
                if request.ab.is_converted(exp):
                    request.ab.convert(exp)
