import multiprocessing

bind = "0.0.0.0:8000"
# workers = multiprocessing.cpu_count() * 2 + 1
workers = 1
reload = True
loglevel = 'info'
errorlog = 'storage/logs/gunicorn.log'

# capture_output = True