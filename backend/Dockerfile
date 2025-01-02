FROM python:3.11

WORKDIR /app

COPY ./requirements.txt /app

RUN pip install -r requirements.txt

COPY . /app

EXPOSE 50001

CMD ["python", "app.py"]