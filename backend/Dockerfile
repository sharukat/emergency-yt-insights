FROM nvidia/cuda:11.8.0-base-ubuntu22.04

WORKDIR /app

COPY ./requirements.txt /app

RUN apt-get update && apt-get install -y \
    python3.11 \
    python3-pip

RUN pip install -r requirements.txt

COPY . /app

EXPOSE 80

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]