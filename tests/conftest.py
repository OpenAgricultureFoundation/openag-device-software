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


#debugrob: get DB creation errors, how do we set the correct postgres DB user?
# give django database access to all tests 
#@pytest.fixture(autouse=True)
#def enable_db_access_for_all_tests(db):
#    pass


