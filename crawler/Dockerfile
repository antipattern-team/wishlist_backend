FROM python:3.7.4

COPY . .

RUN pip install -r requirements.txt

ENV FPS 10
ENV DEBUG 1
ENV FILE "db.txt"

ENV SLEEP 1

CMD ["python", "crawler.py"]