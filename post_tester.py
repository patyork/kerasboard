import requests

import numpy as np

import time

id = 50
while True:
    r = requests.get('http://localhost:8888/api', params={'id':id, 'value':np.random.random()*1000})
    time.sleep(.5)
    id += 1