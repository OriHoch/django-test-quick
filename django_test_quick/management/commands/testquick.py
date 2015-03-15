import logging
import sys
import os
from optparse import make_option, OptionParser

from django.conf import settings
from django.core.management.base import BaseCommand
from django.test.utils import get_runner as django_get_runner
from django.core.management import call_command
from django.test.runner import DiscoverRunner


TESTQUICK_INSTALL = """
######################################################
#                                                    #
# testquick management command                       #
#                                                    #
######################################################
#
# To use this management command you need to create a new db which will be re-used for testing
#
# then need to add some settings in your settings override file:
#
# ENABLE_TESTQUICK = True
# if 'testquick' in sys.argv:
#     DATABASES['default'] = dj_database_url.parse("postgres://username:password@database/dbname")
#
# * Replace the db connection according to your desired db configuration
#
# if you encounter errors relating to migrations - try deleting this db and re-creating it
#
# first time you should run ./manage.py testquick --init
#
# also, if there is a change in mgirations you should run --init
#
#######################################################
"""


class TestQuickDiscoverRunner(DiscoverRunner):

    def setup_databases(self, **kwargs):
        pass

    def teardown_databases(self, old_config, **kwargs):
        pass


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--noinput',
            action='store_false', dest='interactive', default=True,
            help='Tells Django to NOT prompt the user for input of any kind.'),
        make_option('--failfast',
            action='store_true', dest='failfast', default=False,
            help='Tells Django to stop running the test suite after first '
                 'failed test.'),
        make_option('--testrunner',
            action='store', dest='testrunner',
            help='Tells Django to use specified test runner class instead of '
                 'the TestQuickDiscoverRunner'),
        make_option('--init',
            action='store_true', dest='init', default=False,
            help='Initialize the database - you should run this if you get migration / db related errors'),
    )
    help = ('Similar to test management command but runs quicker - mostly by reusing the db')
    args = '[path.to.modulename|path.to.modulename.TestCase|path.to.modulename.TestCase.test_method]...'

    requires_model_validation = False

    def __init__(self):
        self.test_runner = None
        super(Command, self).__init__()

    def run_from_argv(self, argv):
        """
        Pre-parse the command line to extract the value of the --testrunner
        option. This allows a test runner to define additional command line
        arguments.
        """
        option = '--testrunner='
        for arg in argv[2:]:
            if arg.startswith(option):
                self.test_runner = arg[len(option):]
                break
        super(Command, self).run_from_argv(argv)

    def create_parser(self, prog_name, subcommand):
        test_runner_class = self.get_runner(settings, self.test_runner)
        options = self.option_list + getattr(
            test_runner_class, 'option_list', ())
        return OptionParser(prog=prog_name,
                            usage=self.usage(subcommand),
                            version=self.get_version(),
                            option_list=options)

    def execute(self, *args, **options):
        if int(options['verbosity']) > 0:
            # ensure that deprecation warnings are displayed during testing
            # the following state is assumed:
            # logging.capturewarnings is true
            # a "default" level warnings filter has been added for
            # DeprecationWarning. See django.conf.LazySettings._configure_logging
            logger = logging.getLogger('py.warnings')
            handler = logging.StreamHandler()
            logger.addHandler(handler)
        super(Command, self).execute(*args, **options)
        if int(options['verbosity']) > 0:
            # remove the testing-specific handler
            logger.removeHandler(handler)

    def handle(self, *test_labels, **options):
        from django.conf import settings

        if getattr(settings, 'ENABLE_TESTQUICK', None) != True:
            print '\n\nERROR\n\n%s\n\n'%TESTQUICK_INSTALL
            return

        if options.get('init'):
            call_command('syncdb', interactive=False)
            call_command('migrate', fake=True, interactive=False)
            call_command('testquick')
        else:
            TestRunner = self.get_runner(settings, options.get('testrunner'))
            options['verbosity'] = int(options.get('verbosity'))

            test_runner = TestRunner(**options)
            failures = test_runner.run_tests(test_labels)

            if failures:
                sys.exit(bool(failures))

    def get_runner(self, settings, test_runner_class=None):
        if not test_runner_class:
            test_runner_class = 'django_test_quick.management.commands.testquick.TestQuickDiscoverRunner'

        return django_get_runner(settings, test_runner_class)