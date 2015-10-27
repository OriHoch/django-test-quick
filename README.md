# django-test-quick
enhancements for django test management command to run quickly

# Installation
Add to your requirements.txt file:

https://github.com/OriHoch/django-test-quick/archive/v1.2.1.zip

Add to your INSTALLED_APPS:

django_test_quick

run:

./manage.py testquick

To really take advantage of all the features you should also change your test cases base class to django_test_quick.utils.TestCase
