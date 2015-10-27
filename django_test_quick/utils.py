from django.test import TestCase as DjangoTestCase
import django_test_quick


class TestCase(DjangoTestCase):

    def _pre_setup(self):
        if not django_test_quick.TESTQUICK_RUNNING:
            super(TestCase, self)._pre_setup()

    def _post_teardown(self):
        if not django_test_quick.TESTQUICK_RUNNING:
            super(TestCase, self)._post_teardown()


def get_or_create_or_update(Model, **kwargs):
    """
    when using tests which re-use the db, we might want to re-use existing objects in DB as well
    but the problem with get_or_create is that it ignores the defaults parameter if the object already exists
    this command updates the object based on defaults even if it already exists
    """
    defaults = kwargs.get('defaults', {})
    obj, created = Model.objects.get_or_create(**kwargs)
    if not created:
        save = False
        for k,v in defaults.iteritems():
            if v != getattr(obj, k):
                setattr(obj, k, v)
                save = True
        if save:
            obj.save()
    return obj
