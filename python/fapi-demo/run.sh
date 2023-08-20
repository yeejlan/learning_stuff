uvicorn main:app --host 0.0.0.0 --port 8000 --reload --log-config uvicorn.json --no-access-log

# uvicorn main:app --host 0.0.0.0 --port 8000 --reload --no-access-log --use-colors

# gunicorn -k uvicorn.workers.UvicornWorker main:app -c unicorn.conf.py

# install packages
# pip3 install -r /app/requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple


# reload and rotate daily log for gunicorn
# kill -SIGHUP $(pidof gunicorn_manager_porcess)