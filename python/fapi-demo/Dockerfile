FROM python:3.11

RUN apt-get update
RUN apt-get install -y net-tools
RUN apt-get install -y telnet
RUN apt-get install -y iputils-ping

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

COPY ./ /app

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80", "--reload", "--log-config", "uvicorn.json", "--no-access-log"]