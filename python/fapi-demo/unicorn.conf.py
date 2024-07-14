import multiprocessing
from core.logger import getDailyLogName

bind = "0.0.0.0:8000"
workers = multiprocessing.cpu_count() * 2 + 1
reload = False
loglevel = 'info'
errorlog = getDailyLogName('gunicorn')

pidfile = 'storage/gunicorn_pid'