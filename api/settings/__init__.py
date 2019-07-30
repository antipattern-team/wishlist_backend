import os

sleep = False
if 'SLEEP' in os.environ:
    sleep = bool(os.environ['SLEEP'])

es_host = 'localhost'
if 'ESHOST' in os.environ:
    es_host = os.environ['ESHOST']

pg_host = 'localhost'
if 'PGHOST' in os.environ:
    pg_host = os.environ['PGHOST']

pg_database = 'wishlist'
if 'POSTGRES_DB' in os.environ:
    pg_database = os.environ['POSTGRES_DB']

pg_password = ''
if 'POSTGRES_PASSWORD' in os.environ:
    pg_password = os.environ['POSTGRES_PASSWORD']

pg_user = 'postgres'
if 'POSTGRES_USER' in os.environ:
    pg_user = os.environ['POSTGRES_USER']

rmq_host = 'localhost'
if 'RMQHOST' in os.environ:
    rmq_host = os.environ['RMQHOST']

auth_key = '123'
if 'AUTHKEY' in os.environ:
    auth_key = os.environ['AUTHKEY']

app_secret = '123'
if 'APPSECRET' in os.environ:
    app_secret = os.environ['APPSECRET']
