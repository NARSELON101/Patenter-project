FROM python:3.10.14-alpine3.20

COPY ./requirements.txt ./requirements.txt
RUN python -m pip install -r ./requirements.txt
COPY ./ ./app

WORKDIR /app

ENTRYPOINT ["python", "app.py"]