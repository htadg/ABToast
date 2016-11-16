from django.utils.deprecation import MiddlewareMixin

from .abmain import AB
from .models import Experiment


class ABMiddleware(MiddlewareMixin):
    def process_request(self, request):
        request.ab = AB(request)
        if request.ab.is_active():
            exps = Experiment.objects.filter(cancelled=False)
            for exp in exps:
                if exp.is_active:
                    exp.percentage = exp.get_updated_traffic()
                exp.save()
                if request.ab.is_converted(exp):
                    request.ab.convert(exp)
