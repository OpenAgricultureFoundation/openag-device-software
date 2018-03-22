import string, time

from django.contrib.auth.models import User
from django.utils.crypto import get_random_string

from celery import shared_task
from celery.utils.log import get_task_logger


logger = get_task_logger(__name__)


@shared_task
def create_random_user_accounts(total):
    for i in range(total):
        username = 'user_{}'.format(get_random_string(10, string.ascii_letters))
        email = '{}@example.com'.format(username)
        password = get_random_string(50)
        User.objects.create_user(username=username, email=email, password=password)
    return '{} random users created with success!'.format(total)


@shared_task
def printy(value):
    print(value)
    logger.info("Received value: {}".format(value))
    return 'done'




