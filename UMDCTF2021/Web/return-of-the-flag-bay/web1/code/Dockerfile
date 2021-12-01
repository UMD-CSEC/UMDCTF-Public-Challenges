FROM python:3.7.2-alpine
EXPOSE 5000

WORKDIR /code
COPY . .
RUN pip install -r requirements.txt
CMD FLASK_DEBUG=1 python challenge.py --host=0.0.0.0