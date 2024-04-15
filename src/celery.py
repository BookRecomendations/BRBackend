from celery import Celery

app = Celery(
    'tasks',
    broker='redis://127.0.0.1:6379/0',
    backend='redis://127.0.0.1:6379/0'
)
app.autodiscover_tasks(['src.services'], force=True)

# Celery -A src.celery.app worker -l info -P gevent