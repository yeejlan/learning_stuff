import multiprocessing
from core.logger import getDailyLogName

bind = "0.0.0.0:8000"
# workers = multiprocessing.cpu_count() * 2 + 1
workers = 1
reload = True
loglevel = 'info'
errorlog = getDailyLogName('gunicorn')

pidfile = 'storage/gunicorn_pid'