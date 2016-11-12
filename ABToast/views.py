from django.shortcuts import render, render_to_response
from django.template import TemplateDoesNotExist


def home(request, template_name="registrations/signup.html"):
    try:
        template_name = request.ab.run(template_name)
    except TemplateDoesNotExist:
        pass
    return render_to_response(template_name)


def success(request):
    return render(request, template_name="registrations/success.html", context={})
