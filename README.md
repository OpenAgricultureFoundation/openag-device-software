# Django Celery Example

Example used in the blog post [How to Use Celery and RabbitMQ with Django](https://simpleisbetterthancomplex.com/tutorial/2017/08/20/how-to-use-celery-with-django.html?utm_source=github&utm_medium=repository)

## Running Locally

```bash
git clone https://github.com/sibtc/django-celery-example.git
```

```bash
pip install -r requirements.txt
```

```bash
python manage.py migrate
```

```bash
python manage.py runserver
```

```bash
celery -A mysite worker -l info
```

Make sure you have RabbitMQ service running.

```bash
rabbitmq-server
```

For more info see the Blog post.