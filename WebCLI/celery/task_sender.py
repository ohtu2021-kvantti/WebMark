from WebMark.settings import USING_CELERY
from . import celery_app


def send_benchmark_task(*args):
    if USING_CELERY:
        celery_app.send_task("benchmark.benchmark_task", args=args)
