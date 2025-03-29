'''from celery import Celery, Task
from flask import Flask

def celery_init_app():
    celery_app = Celery(
        'applications',
        broker='redis://localhost:6379/0',
        backend='redis://localhost:6379/1',
        include=['applications.task']
    )

    celery_app.conf.update(
        broker_url='redis://localhost:6379/0',
        result_backend='redis://localhost:6379/1',
        task_serializer='json',
        accept_content=['json'],
        result_serializer='json',
        timezone='Asia/Kolkata',
        enable_utc=True
    )

    class FlaskTask(Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery_app.Task = FlaskTask
    return celery_app

app = Flask(__name__)
celery = celery_init_app()'''

from celery import Celery, Task
from flask import current_app as app

def celery_init_app():
    class FlaskTask(Task):
        def __call__(self, *args: object, **kwargs: object):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery_app = Celery()

    return celery_app

celery = celery_init_app()

