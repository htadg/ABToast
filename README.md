# ABToast

ABToast is a simple A/B Testing app that is developed in django. This app implements the Django Session functionality to achieve the goal.

### Installation

ABToast requires [Django](https://www.djangoproject.com/download/) to run.

Install ABToast from pip
```sh
$ pip install django-abtoast
```
OR, Get ABToast locally
```sh
$ git clone https://github.com/htadg/ABToast.git ABToast
```

Add ABToast to INSTALLED_APPS
```python
INSTALLED_APPS = (
    # Django Default Apps
    'django.contrib.admin',
    '...',
    # ABToast
    'ABToast',
)
```
Add ABToast.middleware.ABMiddleware to the project middlewares
```python
MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    '...',
    # Custom Middleware
    'ABToast.middleware.ABMiddleware',
)
```
Migrate the database and create admin account
```sh
$ python manage.py makemigrations
$ python manage.py migrate
$ python manage.py createsuperuser
```
Now Create your own new Tests in the Database
```
Note: You can also create New Experiment and Tests from the Django Admin Panel
```
```python
from datetime import date
from dateutil.relativedelta import relativedelta

from ABToast.models import Experiment, Test


# Starting the Experiment from today
start_date = date.today()
# End Date for the Experiment
# Experiment runs for two months
end_date = start_date + relativedelta(months=+2)

# Create an Experiment
exp = Experiment.objects.create(name="Homepage Test", template_name="registraions/signup.html", goal="registrations/success", start=start_date, end=end_date, is_active=True)

# Create two variations of the homepage.

# One Test for the original template
Test.objects.create(template_name="registrations/signup.html", experiment=exp)

# Other Test for the New Variant
Test.objects.create(template_name="registrations/new_signup.html", experiment=exp)
```
Now You can run A/B Test on a view
```python
def home(request, template_name="registrations/signup.html"):
    try:
        template_name = request.ab.run(template_name)
    except TemplateDoesNotExist:
        pass
    return render_to_response(template_name)
```
### Development

Want to contribute? Great!

Do the necessary changes that you feel and send a pull request.


### Todos

 - [ ] Multivariate Testing
 - [ ] Add Graphical Information
 - [ ] Add Bayesian Formula for the Conversion Rates

License
----

MIT

**Free Software, Hell Yeah!**
