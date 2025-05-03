FROM python:3.13-slim AS app

RUN mkdir /app
WORKDIR /app

ADD . /app/


RUN pip install torch==2.6.0 -i https://download.pytorch.org/whl/cpu
RUN pip install -r requirements.txt

RUN python3 download.py

EXPOSE 6967

CMD ["python3", "server.py"]
