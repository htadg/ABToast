from django.conf.urls import url

import views

urlpatterns = [
    url(r'experiment_details/(?P<experiment_id>\d+)', views.details, name="experiment_details"),
               ]
