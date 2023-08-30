FROM python:3.10-bullseye

EXPOSE 8888

WORKDIR /code
ADD . /code

RUN apt-get update

RUN python -m pip install -r /code/requirements.txt

COPY . .

ENTRYPOINT ["python3", "main.py"]