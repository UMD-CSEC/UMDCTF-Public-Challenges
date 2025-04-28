FROM python:3

WORKDIR /usr/app

COPY . .

RUN pip install --no-cache-dir --upgrade -r /usr/app/requirements.txt

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]