import os, django, pytest
from django.conf import settings

# We manually designate settings we will be using in an environment variable.
# This is similar to what occurs in the `manage.py`
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')

# `pytest` automatically calls this function once when tests are run.
def pytest_configure():
    settings.DEBUG = False
    # If you have any test specific settings, you can declare them here,
    # e.g.
    # settings.PASSWORD_HASHERS = (
    #     'django.contrib.auth.hashers.MD5PasswordHasher',
    # )
    django.setup()


# Give django database access to all tests.
# The alternative is to mark just the test functions that need DB access with:
#    @pytest.mark.django_db
@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    pass


"""
We want django / pytest to recreate a TEST DB each test run, so DON'T 
override the default fixture by using the function below.

Instead look in app/settings.py at the DATABASES / 'default' / 'TEST' section.

# Configure access to our REAL database. Not good for tests, because the DB
# state changes when we run the app!
@pytest.fixture(scope='session')
def django_db_setup():
    settings.DATABASES['default'] = {
        'USER': 'openag',
        'PASSWORD': 'openag',
        'NAME': 'test_openag_brain',
        'ENGINE': 'django.db.backends.postgresql',
    }
"""


