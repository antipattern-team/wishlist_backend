import os

sleep = False
if 'SLEEP' in os.environ:
    sleep = bool(os.environ['SLEEP'])

rmq_host = 'localhost'
if 'RMQHOST' in os.environ:
    rmq_host = os.environ['RMQHOST']

auth_key = '123'
if 'AUTHKEY' in os.environ:
    auth_key = os.environ['AUTHKEY']
