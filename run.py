from decimal import *
import requests
import time
import random
import json 

from flask import Flask
from flask import request, render_template

from flask_caching import Cache

import logging
#log = logging.getLogger('werkzeug')
#log.setLevel(logging.ERROR)

format = '%(asctime)s: %(message)s'
logging.basicConfig(format=format, level=logging.INFO, datefmt='%H:%M:%S')
async_mode = None

config = {
    "DEBUG": True,          # some Flask specific configs
    "CACHE_TYPE": "SimpleCache",  # Flask-Caching related configs
    "CACHE_DEFAULT_TIMEOUT": 300
}
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'

app.config.from_mapping(config)
cache = Cache(app)

url = 'http://127.0.0.1:7076'
conf_active = {'action' : 'confirmation_active'}

@app.route('/elections/all')
@cache.cached(timeout=300)
def all_elections():
    logging.info('Running...')
    x = requests.post(url, json = conf_active)
    result = x.json()
    confs = result['confirmations']
    total_confs = int(result['unconfirmed'])

    all = []
    total_roots = 0
    total_votes = 0
    buckets = [0 for _ in range(129)]
    for root in confs:
        conf_command = {'action' : 'confirmation_info', 'json_block': 'true', 'root': root ,'representatives': 'true'}
        x = requests.post(url, json = conf_command)
        result = x.json()

        if 'last_winner' in result:
            last_winner = result['last_winner']

            if 'total_tally' in result:
                total_tally = result['total_tally']
                total_votes = total_votes + int(total_tally)
            balance = result['blocks'][last_winner]['contents']['balance']
            bucket_balance = len(balance)
            buckets[bucket_balance] = int(buckets[bucket_balance]) + 1
            total_roots = total_roots + 1
    avg_votes = Decimal(total_votes) / Decimal(total_roots)


    bucket_index = 0
    for bucket in buckets:
        all.append('{ y: ' + str(bucket) + ', label: "' + str(bucket_index) + '" }')
        bucket_index = bucket_index + 1

    new_all = str(all)
    replace_new_all = new_all.replace('\'', '')
    logging.info(replace_new_all)
#    return '<html><br>Total Roots: {}<br>Total_Votes: {}<br>Avg Votes: {:f}<br><br>{}</html>'.format(total_roots, total_votes, avg_votes, all)
    logging.info('Done')
    return render_template('index.html', bucket_data=replace_new_all)
