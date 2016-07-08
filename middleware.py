from threading import local

from .abmain import AB
from .models import Experiment


_thread_locals = local()


def get_current_request():
    return getattr(_thread_locals, 'request', None)


class ABMiddleware:
    def process_request(self, request):
        _thread_locals.request = request
        request.ab = AB(request)
        if request.ab.is_active():
            exps = Experiment.objects.all()
            for exp in exps:
                if request.ab.is_converted(exp):
                    request.ab.convert(exp)
