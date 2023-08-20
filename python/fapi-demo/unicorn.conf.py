import multiprocessing
from log import get_daily_log_name

bind = "0.0.0.0:8000"
# workers = multiprocessing.cpu_count() * 2 + 1
workers = 1
reload = True
loglevel = 'info'
errorlog = get_daily_log_name('gunicorn')

pidfile = 'storage/gunicorn_pid'