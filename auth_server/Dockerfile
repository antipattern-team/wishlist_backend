FROM python:3.7.4

COPY . .

RUN pip install -r requirements.txt

ENV SLEEP 1

CMD ["python", "auth_server.py"]