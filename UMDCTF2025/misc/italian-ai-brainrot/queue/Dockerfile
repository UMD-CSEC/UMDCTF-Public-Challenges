FROM python:3.9

RUN mkdir /app
WORKDIR /app

ADD . /app/

RUN pip install Flask==3.1.0
EXPOSE 5000

CMD ["python3", "app.py"]
